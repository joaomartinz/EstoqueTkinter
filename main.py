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

                       