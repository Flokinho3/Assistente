import ctypes
import os
import keyboard
import time
import speech_recognition as sr
import pyttsx3  # Biblioteca para conversão de texto em fala
import sys
import threading
import pystray  # Para criar o ícone na bandeja do sistema
from pystray import MenuItem as item
from PIL import Image, ImageDraw  # Para criar o ícone (imagem)

# Adiciona o diretório onde IA.py está localizado (uma pasta acima de SEM_GUI) ao sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from IA import GEMINI

def ocultar_console():
    """Oculta a janela do console no Windows."""
    if os.name == 'nt':  # Verifica se o sistema operacional é Windows
        ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)

def cria_imagem():
    """Cria a imagem do ícone (imagem simples)."""
    try:
        img = "Sistema/Fundo_barra.png"  # Certifique-se de que o caminho está correto
        image = Image.open(img)
    except FileNotFoundError:
        # Se não encontrar a imagem, cria uma simples
        image = Image.new('RGB', (64, 64), color=(255, 0, 0))  # Faz um ícone simples (vermelho)
    return image

def fala_gemini(texto):
    """Converte o texto de resposta do GEMINI em áudio e fala."""
    engine = pyttsx3.init()  # Inicializa o motor de texto para fala
    engine.setProperty('rate', 150)  # Velocidade da fala (ajuste conforme necessário)
    engine.setProperty('volume', 1)  # Volume da fala (ajuste conforme necessário)
    
    # Filtra os caracteres indesejados do texto antes de passar para a fala
    texto = texto.replace("**", "").replace("* **", "")  # Remove os filtros desejados
    
    def speak():
        engine.say(texto)  # Passa o texto que o GEMINI respondeu
        engine.runAndWait()  # Executa a fala

    # Inicia a fala em uma thread separada para permitir interrupção
    speak_thread = threading.Thread(target=speak)
    speak_thread.start()

    # Aguarda até que o usuário pressione a tecla de interrupção para parar a fala
    while speak_thread.is_alive():
        if keyboard.is_pressed('ctrl+alt+z'):  # Detecta 'Ctrl+Alt+Z' para parar a fala
            print("Interrompendo a fala...")
            engine.stop()  # Interrompe a fala
            speak_thread.join()  # Espera até que a thread de fala tenha terminado
            break

def ativar_audio():
    """Captura áudio do microfone e tenta reconhecer fala."""
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Gravando... Fale algo.")
        try:
            audio = r.listen(source, timeout=9999)  # Captura áudio por até 5 segundos
            texto = r.recognize_google(audio, language="pt-BR")  # Reconhece fala em português
            print(f"Texto reconhecido: {texto}")
            gemini = GEMINI()  # Instancia a classe GEMINI sem argumentos
            resposta = gemini.enviar(texto)  # Chama o método 'enviar' para processar a fala
            print(f"Resposta do GEMINI: {resposta}")
            fala_gemini(resposta)  # Envia a resposta para o GEMINI falar
        except sr.WaitTimeoutError:
            print("Nenhum som detectado. Tempo limite esgotado.")
        except sr.UnknownValueError:
            print("Não foi possível entender o áudio.")
        except sr.RequestError as e:
            print(f"Erro ao acessar o serviço de reconhecimento: {e}")

def sair(icon, item):
    """Função para sair quando o item do menu for clicado"""
    icon.stop()
    sys.exit()

def on_activate_fala(icon, item):
    """Ativa o reconhecimento de fala"""
    ativar_audio()

def on_stop_fala(icon, item):
    """Parar a fala"""
    print("Fala parada")

import os

def informacoes(icon, item):
    """Função de informações para o menu"""
    INFOR = """Ativar o áudio:
    - Segure a combinação de teclas: Ctrl + Alt + A
    - Isso manterá o áudio ativo até que você desative
    - Atraso de 0.5s para ativar o áudio\n

    Desativar o áudio:
    - Solte a combinação de teclas: Ctrl + Alt + A
    - Isso desativará o áudio\n

    Parar fala:
    - Segure a combinação de teclas: Ctrl + Alt + Z
    - Isso fará com que o programa pare de falar o texto 
    - Atraso de 0.5s para falar"""
    
    # Salva as informações em um arquivo temporário
    file_path = "informacoes.txt"
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(INFOR)
    
    # Abre o arquivo de informações
    os.startfile(file_path)


def criar_tray_icon():
    """Cria o ícone da bandeja do sistema"""
    icon_image = cria_imagem()
    icon = pystray.Icon("GEMINI Assistant", icon_image, menu=(
        item("Ativar Fala", on_activate_fala),
        item("Parar Fala", on_stop_fala),
        item("Informações", informacoes),
        item("Sair", sair),
    ))
    icon.run()

def main():
    """Oculta o console e inicia a detecção de teclas."""
    ocultar_console()
    print("Aperte 'Ctrl + Alt + A' para ativar o reconhecimento de áudio.")
    
    # Cria o ícone da bandeja do sistema
    threading.Thread(target=criar_tray_icon, daemon=True).start()

    while True:
        if keyboard.is_pressed('ctrl+alt+a'):
            ativar_audio()
            time.sleep(1)  # Aguarda um segundo para evitar múltiplas ativações

if __name__ == '__main__':
    main()
