import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import pandas as pd
from sqlalchemy import text
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os 

# === Carrega dados env ===
load_dotenv()

user = os.getenv("DB_USER")
password = os.getenv("DB_PASSWORD")
host = os.getenv("DB_HOST")
port = os.getenv("DB_PORT", "3306")
database = os.getenv("DB_NAME")

engine = create_engine(f"mysql+mysqlconnector://{user}:{password}@{host}:{port}/{database}")
produtos = pd.read_sql("SELECT * FROM produtos", engine)
fornecedores = pd.read_sql("SELECT * FROM Fornecedores", engine)
movimentacoes = pd.read_sql("SELECT * FROM Movimentacao", engine)

# === Função utilitária para mostrar DataFrame em Treeview com scroll ===
def mostrar_dataframe(df: pd.DataFrame, titulo: str):
    if df is None or df.empty:
        messagebox.showinfo(titulo, "Sem dados para exibir")
        return

janela = tk.Toplevel(root)
janela.title(titulo)

frame = ttk.Frame(janela)
frame.pack(fill="both", expand=True)

cols = list(df.columns)
tree = ttk.Treeview(frame, columns=cols, show="headings")

vsb = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
tree.configure(yscrollcommand=vsb.set)
vsb.pack(side="right", fill="y")

hsb = ttk.Scrollbar(frame, orient="horizontal", command=tree.xview)
tree.configure(xscrollcommand=hsb.set)
hsb.pack(side="bottom", fill="x")

tree.pack(fill="both", expand=True)

for col in cols:
    tree.heading(col, text=col)
    tree.column(col, width=120, anchor="w")

for _, row in df.iterrows():
    vals = [("" if pd.isna(v) else str(v)) for v in row.tolist()]
    tree.insert("", "end", values=vals)

janela.geometry("800x400")

def ver_estoque():
    mostrar_dataframe(produtos, "Estoque Atual")

def informacoes_fornecedores():
    mostrar_dataframe(fornecedores, "Informações dos Fornecedores")

def exportar():
    escolha = simpledialog.askstring("Exportar", "Escolha:\n1 - Produtos\n2 - Movimentações")
    if escolha not in ("1", "2"):
        messagebox.showerror("Opção inválida!")
        return
    if escolha == "1":
        df = produtos
        nome = "produtos"
    elif escolha == "2":
        df = movimentacoes
        nome = "movimentacoes"
    formato = simpledialog.askstring("Formato", "Formato: csv ou xlsx").strip().lower()
    try:
        if formato == "csv":
            df.to_csv(f"{nome}.csv", index=False)
            messagebox.showinfo("Exportar", f"Arquivo {nome}.csv salvo.")
        elif formato == "xlsx":
            df.to_excel(f"{nome}.xlsx", index=False)
            messagebox.showinfo("Exportar", f"Arquivo {nome} salvo.")
        else:
            messagebox.showerror("Opção inválida")
    except Exception as e:
        messagebox.showerror("Erro ao exportar", str(e))
            
def buscar_produto_gui():
    popup = tk.Toplevel(root)
    popup.title("Buscar produto")
    popup.geometry("420x160")

    modo = tk.StringVar(value="nome")
    rb1 = tk.Radiobutton(popup, text="buscar por nome(parcial)", variable=modo, value="nome")
    rb2 = tk.Radiobutton(popup, text="Buscar por ID (exato)", variable=modo, value="id")
    rb1.pack(anchor="w", padx=10, pady=2)
    rb2.pack(anchor="w", padx=10, pady=2)

    lbl = tk.Label(popup, text="Termo de busca")
    lbl.pack(anchor="w", padx=10)
    entrada = tk.Entry(popup, width=50)
    entrada.pack(padx=10, pady=6)

    def executar_busca():
        termo = entrada.get().strip()
        if not termo:
            messagebox.showwarning("Aviso", "Digite um termo para buscar")
            return
        if modo.get() == "id":
            try:
                pid = int(termo)
            except ValueError:
                messagebox.showerror("ID inválido.")
            resultado = produtos[produtos["id_produto"] == pid]
        else:
            resultado = produtos[produtos["nome"].str.lower().str.contains(termo.lower(), na=False)]
        
        if resultado.empty:
                messagebox.showinfo("Nenhum produto encontrado.")
                return
        
        mostrar_dataframe(resultado, f"Resultados da busca ({len(resultado)})")
        popup.destroy()

    btn_buscar = tk.Button(popup, text="Buscar", command=executar_busca)
    btn_buscar.pack(pady=8)

def adicionar_produto():
    popup = tk.Toplevel(root)
    popup.title("Adicionar produto")
    popup.geometry("420x160")

    
    lbl_id = tk.Label(popup, text="ID do produto")
    lbl_id.pack(anchor="w", padx=10)
    entrada_id = tk.Entry(popup, width=50)
    entrada_id.pack(padx=10, pady=6)

    lbl_qtd = tk.Label(popup, text="Quantidade a adicionar")
    lbl_qtd.pack(anchor="w", padx=10)
    entrada_qtd = tk.Entry(popup, width=50)
    entrada_qtd.pack(padx=10, pady=6)
    
    def executar_adicao():
        pid = entrada_id.get().strip()
        qtd = entrada_qtd.get().strip()

        if not pid or not qtd:
            messagebox.showerror("Preencha todos os campos.")
            return

        try:
            pid = int(pid)
            qtd = int(qtd)
        except ValueError:
            messagebox.showerror("ID e quantidade devem ser números inteiros")
            return
        if qtd <= 0:
            messagebox.showerror("A quantidade deve ser maior que zero.")   
            return
        
        try:
            with engine.begin() as conn:
                conn.execute(
                    text("UPDATE produtos SET quantidade_estoque_atual = quantidade_estoque_atual + qtd WHERE id_produto = :pid"),
                    {"qtd": qtd, "pid": pid}

            global produtos
            produtos = pd.read_sql("SELECT * FROM produtos", engine)

            messagebox.showinfo("Sucesso", f"{qtd} unidades adicionadas ao produto {pid}.")
            popup.destroy()

                )
        except Exception as e:
            messagebox.showerror(f"Falha ao atualizar: {e}")

    btn_confirmar = tk.Button(popup, text="Confirmar", command=executar_adicao)
    btn_confirmar.pack(pady=8)

def cadastrar_produto():
    popup = tk.Toplevel(root)
    popup.title("Cadastrar produto")
    popup.geometry("420x160")

    lbl_nome = tk.Label(popup, text="Nome do produto")
    lbl_nome.pack(anchor="w", padx=10)
    entrada_nome = tk.Entry(popup, width=50)
    entrada_nome.pack(padx=10, pady=6)
    
    lbl_cat = tk.Label(popup, text="Categoria")
    lbl_cat.pack(anchor="w", padx=10)
    entrada_cat = tk.Entry(popup, width=50)
    entrada_cat.pack(padx=10, pady=6)

    lbl_qtd = tk.Label(popup, text="Quantidade")
    lbl_qtd.pack(anchor="w", padx=10)
    entrada_qtd= tk.Entry(popup, width=50)
    entrada_qtd.pack(padx=10, pady=6)

    lbl_preco = tk.Label(popup, text="Preço unitário")
    lbl_preco.pack(anchor="w", padx=10)
    entrada_preco = tk.Entry(popup, width=50)
    entrada_preco.pack(padx=10, pady=6)

    lbl_forn = tk.Label(popup, text="ID do fornecedor")
    lbl_forn.pack(anchor="w", padx=10)
    entrada_forn = tk.Entry(popup, width=50)
    entrada_forn.pack(padx=10, pady=6)

    def executar_cadastro():
        nome = entrada_nome.get().strip()
        qtd = entrada_qtd.get().strip()
        categoria = entrada_cat.get().strip()
        preco = entrada_preco.get().strip()
        forn = entrada_forn.get().strip()

        if not nome or not categoria or not qtd or not preco or not forn:
            messagebox.showerror("Preencha todos os campos.") 
            return

        try:
            qtd = int(qtd)
            preco = int(preco)
            forn = int(forn) 
        except ValueError:
            messagebox.showerror("OS valores devem ser númericos")
            return

        if qtd < 0 or preco < 0:
            messagebox.showerror("Quantidade e preço devem ser maiores que zero.")

        try:
            with engine.begin() as conn:
                conn.execute(
                    text("INSERT INTO produtos (nome, categoria, quantidade_estoque_atual, preco_unitario, id_Fornecedor) VALUES (:nome, :cat, :qtd, :preco, :forn)"),
                    {"nome": nome, "cat": categoria "qtd": qtd, "preco": preco, "forn": forn}
                ) 
            global produtos
            produtos = pd.read_sql("SELECT * FROM produtos", engine)

            messagebox.showinfo(f"Produto {nome} cadastrado.")
            popup.destroy()

        except Exception as e:
            messagebox.showerror("Falha ao cadastrar: {e}")

    btn_confirmar = tk.Button(popup, text="Cadastrar", command=executar_cadastro)
    btn_confirmar.pack(pady=10)

       




    
    








        
