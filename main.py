import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import pandas as pd
import matplotlib as plt
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
movimentacao = pd.read_sql("SELECT * FROM Movimentacao", engine)

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