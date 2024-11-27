import ctypes
import os
import keyboard
import time
import speech_recognition as sr
import sys

# Adiciona o diretório onde IA.py está localizado (uma pasta acima de SEM_GUI) ao sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from IA import GEMINI

def ocultar_console():
    """Oculta a janela do console no Windows."""
    if os.name == 'nt':  # Verifica se o sistema operacional é Windows
        ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)

def enviar(fala):
    """Envia a fala para o assistente virtual."""
    resposta = GEMINI(fala)
    print(resposta)

def ativar_audio():
    """Captura áudio do microfone e tenta reconhecer fala."""
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Gravando... Fale algo.")
        try:
            audio = r.listen(source, timeout=9999)  # Captura áudio por até 5 segundos
            texto = r.recognize_google(audio, language="pt-BR")  # Reconhece fala em português
            enviar(texto)
        except sr.WaitTimeoutError:
            print("Nenhum som detectado. Tempo limite esgotado.")
        except sr.UnknownValueError:
            print("Não foi possível entender o áudio.")
        except sr.RequestError as e:
            print(f"Erro ao acessar o serviço de reconhecimento: {e}")

def main():
    """Oculta o console e inicia a detecção de teclas."""
    ocultar_console()
    print("Aperte 'Ctrl + Alt + A' para ativar o reconhecimento de áudio.")
    
    audio_ativo = False  # Flag para controlar o estado do áudio

    while True:
        if keyboard.is_pressed('ctrl+alt+a') and not audio_ativo:
            # Se as teclas forem pressionadas e o áudio ainda não estiver ativo
            audio_ativo = True
            ativar_audio()  # Inicia a captura de áudio
        elif not keyboard.is_pressed('ctrl+alt+a') and audio_ativo:
            # Se as teclas não estiverem pressionadas e o áudio estiver ativo
            audio_ativo = False
            print("Áudio desativado.")  # Indica que o áudio foi desativado

        time.sleep(0.1)  # Atraso para evitar loop excessivo

if __name__ == '__main__':
    main()
