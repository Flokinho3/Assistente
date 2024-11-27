import os
import subprocess
from tkinter import messagebox

# Constantes
PASTA_SISTEMA = "Sistema"
ARQUIVO_VERIFICADO = "Verificado.txt"
ARQUIVO_REQUERIMENTOS = "requirements.txt"

def instalar_dependencias():
    """
    Instala dependências do arquivo requirements.txt.
    """
    try:
        print("Instalando dependências...")
        subprocess.check_call(["pip", "install", "-r", os.path.join(PASTA_SISTEMA, ARQUIVO_REQUERIMENTOS)])
        with open(os.path.join(PASTA_SISTEMA, ARQUIVO_VERIFICADO), "w") as file:
            file.write("Verificado")
        print("Dependências instaladas com sucesso!")
        messagebox.showinfo("Aviso", "Dependências instaladas com sucesso!")
    except Exception as e:
        print(f"Erro ao instalar dependências: {e}")
        messagebox.showerror("Erro", f"Falha ao instalar dependências: {e}")

def iniciar_sistema():
    """
    Pergunta ao usuário como iniciar o sistema e executa o comando correspondente.
    """
    resposta = messagebox.askquestion("Aviso", "Deseja iniciar o sistema com janela?")
    comando = "python GUI/main.py" if resposta == "yes" else "python SEM_GUI/main.py"
    try:
        subprocess.run(comando, shell=True)
    except Exception as e:
        print(f"Erro ao iniciar o sistema: {e}")
        messagebox.showerror("Erro", f"Falha ao iniciar o sistema: {e}")

def main():
    print("Iniciando sistema...")
    
    # Verifica se a pasta do sistema existe
    if not os.path.exists(PASTA_SISTEMA):
        os.makedirs(PASTA_SISTEMA)
        

    # Verifica se o arquivo requirements.txt existe
    if not os.path.exists(os.path.join(PASTA_SISTEMA, ARQUIVO_REQUERIMENTOS)):
        messagebox.showinfo("Aviso", "Dependências não encontradas!\nNão é possível garantir o funcionamento do sistema.")
        messagebox.showinfo("Aviso", "Recomendado o uso do python 3.11 para evitar erros de compatibilidade.")
        

    # Verifica se já foi instalado
    if not os.path.exists(os.path.join(PASTA_SISTEMA, ARQUIVO_VERIFICADO)):
        messagebox.showinfo("Aviso", "Instalando dependências...")
        messagebox.showinfo("Aviso", "Recomendado o uso do python 3.11 para evitar erros de compatibilidade.")
        instalar_dependencias()

    else:
        messagebox.showinfo("Aviso", "Dependências já instaladas!")

    iniciar_sistema()

if __name__ == "__main__":
    main()
