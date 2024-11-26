import tkinter as tk
import os
from IA import GEMINI

IA = GEMINI()

janela = tk.Tk()
janela.title("Janela Principal")
janela.geometry("600x500")

# Função para exibir a conversa armazenada
def exibir_conversa():
    arquivo = "Conversas/Conversa1.txt"
    if os.path.exists(arquivo):
        with open(arquivo, "r") as f:
            return f.read()
    else:
        conversa_inicial = "Personalidade: Seja voce :3.\n"
        with open(arquivo, "w") as f:
            f.write(conversa_inicial)
        return conversa_inicial

# Função para salvar a conversa
def salvar_conversa(texto):
    arquivo = "Conversas/Conversa1.txt"
    if not os.path.exists("Conversas"):
        os.makedirs("Conversas")

    with open(arquivo, "a") as f:
        f.write(texto + "\n")

# Função para enviar a mensagem e gerar a resposta
def enviar(texto_usuario):
    contexto = exibir_conversa()

    # Chama a IA para gerar a resposta
    resposta = IA.enviar(f"Contexto:\n{contexto}\nUsuário: {texto_usuario}\nCom isso, responda:")
    
    # Salva a interação
    salvar_conversa(f"Usuário: {texto_usuario}")
    salvar_conversa(f"IA: {resposta}")
    
    return resposta


# Função para atualizar a conversa e formatar o texto
def atualizar_conversa():
    mensagens.config(state=tk.NORMAL)  # Permite edição
    mensagens.delete("1.0", tk.END)  # Limpa a caixa de texto
    conversa = exibir_conversa().strip().split("\n")  # Carrega a conversa
    for i, linha in enumerate(conversa):
        tag = "corpo_IA" if i % 2 else "corpo"  # Alterna a formatação
        mensagens.insert(tk.END, linha + "\n", tag)  # Insere a linha formatada            
    mensagens.config(state=tk.DISABLED)  # Torna somente leitura

# Função para lidar com a entrada do usuário
def enviar_mensagem():
    texto_usuario = entrada_texto.get().strip()
    if texto_usuario:  # Verifica se há algo para enviar
        resposta = enviar(texto_usuario)  # Envia a mensagem
        atualizar_conversa()  # Atualiza a conversa exibida
        entrada_texto.delete(0, tk.END)  # Limpa o campo de entrada

# Configurações da interface
painel = tk.Frame(janela, bg="#ADD8E6")  # Cor mais suave
painel.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

# Caixa de exibição de conversa (não editável)
mensagens = tk.Text(painel, font=("Arial", 12), wrap=tk.WORD, height=15)
mensagens.pack(fill=tk.BOTH, expand=True, pady=10)
mensagens.config(state=tk.DISABLED)  # Torna o campo somente leitura

# Configurações de tags para formatação
mensagens.tag_configure("titulo", font=("Arial", 16, "bold"), justify="center")  # Título centralizado e maior
mensagens.tag_configure("subtitulo", font=("Arial", 14, "italic"), lmargin1=30)  # Subtítulo com indentação
mensagens.tag_configure("corpo", font=("Arial", 12))  # Corpo normal
mensagens.tag_configure("corpo_IA", font=("Arial", 12), foreground="blue")  # Corpo da IA com cor diferente
mensagens.tag_configure("italico", font=("Arial", 12, "italic"))  # Tag para texto itálico

# Caixa de entrada para digitar mensagens
entrada_texto = tk.Entry(painel, font=("Arial", 12))
entrada_texto.pack(fill=tk.X, pady=10)

# Botão de envio
enviar_button = tk.Button(painel, text="Enviar", font=("Arial", 12), command=enviar_mensagem)
enviar_button.pack(fill=tk.X, pady=10)

# Carrega a conversa inicial
atualizar_conversa()

# Inicia o loop principal da interface gráfica
janela.mainloop()
