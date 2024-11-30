import tkinter as tk
from tkinter import ttk, messagebox
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from IA import GEMINI

IA = GEMINI()

# Constantes
FILE_CONVERSA = "Conversas/"
if not os.path.exists(FILE_CONVERSA):
    os.makedirs(FILE_CONVERSA)

class GEMINIApp:
    def __init__(self, root):
        self.root = root
        self.root.title("GEMINI")
        self.root.geometry("800x600")
        self.root.configure(bg="#2c3e50")  # Fundo escuro para estética

        self.Chat_atual = None
        self.texto = None
        self.entrada = None

        self.setup_UI()

    def setup_UI(self):
        self.setup_sidebar()
        self.setup_chat_area()
        self.setup_input_area()

    def setup_sidebar(self):
        sidebar = tk.Frame(self.root, width=200, bg="#34495e")
        sidebar.grid(row=0, column=0, rowspan=2, sticky="ns")

        btn_novo = ttk.Button(sidebar, text="Novo", command=self.Iniciar)
        btn_novo.pack(fill="x", pady=5, padx=10)

        btn_abrir = ttk.Button(sidebar, text="Abrir", command=self.Abrir)
        btn_abrir.pack(fill="x", pady=5, padx=10)

        btn_apagar = ttk.Button(sidebar, text="Apagar", command=self.Apagar)
        btn_apagar.pack(fill="x", pady=5, padx=10)

        btn_sair = ttk.Button(sidebar, text="Sair", command=self.root.quit)
        btn_sair.pack(fill="x", pady=5, padx=10)

    def setup_chat_area(self):
        chat_frame = tk.Frame(self.root, bg="#ecf0f1")
        chat_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        self.texto = tk.Text(chat_frame, wrap="word", bg="#ecf0f1", fg="#2c3e50", font=("Arial", 12))
        self.texto.pack(side="left", fill="both", expand=True, padx=5, pady=5)

        scrollbar = tk.Scrollbar(chat_frame, command=self.texto.yview)
        self.texto["yscrollcommand"] = scrollbar.set
        scrollbar.pack(side="right", fill="y")

    def setup_input_area(self):
        input_frame = tk.Frame(self.root, bg="#2c3e50")
        input_frame.grid(row=1, column=1, sticky="ew", padx=10, pady=(0, 10))

        self.entrada = ttk.Entry(input_frame, font=("Arial", 12))
        self.entrada.pack(side="left", fill="x", expand=True, padx=5)

        btn_enviar = ttk.Button(input_frame, text="Enviar", command=self.Enviar)
        btn_enviar.pack(side="right", padx=5)

        # Configurações de redimensionamento
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=0)
        self.root.grid_columnconfigure(1, weight=1)

    def Enviar(self):
        mensagem = self.entrada.get()
        if mensagem.strip():
            self.texto.insert("end", f"Você: {mensagem}\n")
            self.entrada.delete(0, "end")

            # Salva e processa a conversa
            if self.Chat_atual:
                with open(FILE_CONVERSA + self.Chat_atual, "a") as f:
                    f.write(f"Você: {mensagem}\n")

                with open(FILE_CONVERSA + self.Chat_atual, "r") as f:
                    conversa = f.readlines()

                resposta = IA.enviar(conversa)
                self.texto.insert("end", f"GEMINI: {resposta}\n")

                with open(FILE_CONVERSA + self.Chat_atual, "a") as f:
                    f.write(f"GEMINI: {resposta}\n")
        else:
            messagebox.showinfo("Erro", "Mensagem não pode estar vazia!")

    def Iniciar(self):
        nova_conversa = tk.Toplevel(self.root)
        nova_conversa.title("Nova Conversa")
        nova_conversa.geometry("400x300")
        nova_conversa.configure(bg="#ecf0f1")

        tk.Label(nova_conversa, text="Nome da conversa:", bg="#ecf0f1", fg="#2c3e50").pack(pady=10)
        nome = ttk.Entry(nova_conversa)
        nome.pack(pady=5)

        tk.Label(nova_conversa, text="Personalidade (Opcional):", bg="#ecf0f1", fg="#2c3e50").pack(pady=10)
        personalidade = tk.Text(nova_conversa, height=5, width=40)
        personalidade.pack(pady=5)

        def salvar():
            nome_conversa = nome.get().strip()
            if not nome_conversa:
                messagebox.showinfo("Erro", "Nome da conversa não pode ser vazio!")
                return
            if os.path.exists(FILE_CONVERSA + nome_conversa + ".txt"):
                messagebox.showinfo("Erro", "Já existe uma conversa com esse nome!")
                return

            with open(FILE_CONVERSA + nome_conversa + ".txt", "w") as f:
                f.write(personalidade.get("1.0", "end").strip())

            self.Chat_atual = nome_conversa + ".txt"
            self.texto.delete("1.0", "end")
            messagebox.showinfo("Sucesso", "Conversa criada com sucesso!")
            nova_conversa.destroy()

        ttk.Button(nova_conversa, text="Criar", command=salvar).pack(pady=20)

    def Abrir(self):
        arquivos = [f for f in os.listdir(FILE_CONVERSA) if f.endswith(".txt")]
        if not arquivos:
            messagebox.showinfo("Erro", "Nenhuma conversa encontrada!")
            return

        janela_abrir = tk.Toplevel(self.root)
        janela_abrir.title("Abrir Conversa")
        janela_abrir.geometry("300x400")
        janela_abrir.configure(bg="#ecf0f1")

        lista = tk.Listbox(janela_abrir, bg="#ecf0f1", fg="#2c3e50")
        lista.pack(fill="both", expand=True, padx=10, pady=10)
        for arquivo in arquivos:
            lista.insert("end", arquivo)

        def abrir():
            selecionado = lista.get(lista.curselection())
            with open(FILE_CONVERSA + selecionado, "r") as f:
                conteudo = f.read()

            self.Chat_atual = selecionado
            self.texto.delete("1.0", "end")
            self.texto.insert("end", conteudo)
            janela_abrir.destroy()

        ttk.Button(janela_abrir, text="Abrir", command=abrir).pack(pady=10)

    def Apagar(self):
        arquivos = [f for f in os.listdir(FILE_CONVERSA) if f.endswith(".txt")]
        if not arquivos:
            messagebox.showinfo("Erro", "Nenhuma conversa encontrada!")
            return

        janela_apagar = tk.Toplevel(self.root)
        janela_apagar.title("Apagar Conversa")
        janela_apagar.geometry("300x400")
        janela_apagar.configure(bg="#ecf0f1")

        lista = tk.Listbox(janela_apagar, bg="#ecf0f1", fg="#2c3e50")
        lista.pack(fill="both", expand=True, padx=10, pady=10)
        for arquivo in arquivos:
            lista.insert("end", arquivo)

        def apagar():
            selecionado = lista.get(lista.curselection())
            os.remove(FILE_CONVERSA + selecionado)
            if self.Chat_atual == selecionado:
                self.Chat_atual = None
                self.texto.delete("1.0", "end")
            messagebox.showinfo("Sucesso", f"Conversa '{selecionado}' apagada!")
            janela_apagar.destroy()

        ttk.Button(janela_apagar, text="Apagar", command=apagar).pack(pady=10)

# Executa o programa
janela = tk.Tk()
app = GEMINIApp(janela)
janela.mainloop()
