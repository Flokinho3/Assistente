import os
import subprocess
from tkinter import messagebox

# Constantes
PASTA_SISTEMA = "Sistema"
ARQUIVO_VERIFICADO = "Verificado.txt"
ARQUIVO_REQUERIMENTOS = "requirements.txt"

# Obtém o diretório absoluto do script atual
DIRETORIO_ATUAL = os.path.dirname(os.path.abspath(__file__))
PASTA_SISTEMA_ABS = os.path.join(DIRETORIO_ATUAL, PASTA_SISTEMA)


def instalar_dependencias():
    """
    Instala dependências do arquivo requirements.txt.
    """
    try:
        print("Instalando dependências...")
        caminho_requisitos = os.path.join(PASTA_SISTEMA_ABS, ARQUIVO_REQUERIMENTOS)
        subprocess.check_call(["pip", "install", "-r", caminho_requisitos])
        with open(os.path.join(PASTA_SISTEMA_ABS, ARQUIVO_VERIFICADO), "w") as file:
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
    comando = (
        f"python {os.path.join(DIRETORIO_ATUAL, 'GUI', 'main.py')}"
        if resposta == "yes"
        else f"python {os.path.join(DIRETORIO_ATUAL, 'SEM_GUI', 'main.py')}"
    )
    try:
        subprocess.run(comando, shell=True)
    except Exception as e:
        print(f"Erro ao iniciar o sistema: {e}")
        messagebox.showerror("Erro", f"Falha ao iniciar o sistema: {e}")


def main():
    print("Iniciando sistema...")
    
    # Verifica se a pasta do sistema existe
    if not os.path.exists(PASTA_SISTEMA_ABS):
        os.makedirs(PASTA_SISTEMA_ABS)

    # Verifica se o arquivo requirements.txt existe
    caminho_requisitos = os.path.join(PASTA_SISTEMA_ABS, ARQUIVO_REQUERIMENTOS)
    if not os.path.exists(caminho_requisitos):
        messagebox.showinfo("Aviso", "Dependências não encontradas!\nNão é possível garantir o funcionamento do sistema.")
        messagebox.showinfo("Aviso", "Recomendado o uso do Python 3.11 para evitar erros de compatibilidade.")

    # Verifica se já foi instalado
    caminho_verificado = os.path.join(PASTA_SISTEMA_ABS, ARQUIVO_VERIFICADO)
    if not os.path.exists(caminho_verificado):
        messagebox.showinfo("Aviso", "Instalando dependências...")
        instalar_dependencias()
    else:
        messagebox.showinfo("Aviso", "Dependências já instaladas!")

    iniciar_sistema()


if __name__ == "__main__":
    main()
