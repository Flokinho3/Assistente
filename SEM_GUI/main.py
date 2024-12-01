import ctypes
import os
import keyboard
import time
import speech_recognition as sr
import pyttsx3
import sys
import threading
import pystray
from pystray import MenuItem as item
from PIL import Image, ImageDraw
import subprocess
import re
from queue import Queue

# Caminho para os comandos
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
FILE_COMANDOS = os.path.join(BASE_DIR, "SEM_GUI", "Comandos") + os.sep
audio_ativo = False  # Controle do áudio

# Adiciona o diretório onde o script GEMINI está localizado
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from IA import GEMINI

# Fila para gerenciar o processamento de fala
fala_fila = Queue()

def ocultar_console():
    """Oculta a janela do console no Windows."""
    if os.name == 'nt':  # Verifica se é Windows
        ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)

def cria_imagem():
    """Cria ou carrega a imagem do ícone da bandeja."""
    img_path = os.path.join(BASE_DIR, "Sistema", "Fundo_barra.png")
    try:
        image = Image.open(img_path)
    except FileNotFoundError:
        image = Image.new('RGB', (64, 64), color=(255, 0, 0))  # Ícone simples em vermelho
    return image

def filtro_comando(texto):
    """Filtra e executa comandos internos no texto."""
    comandos = [comando.split(".")[0] for comando in os.listdir(FILE_COMANDOS)
                if comando.endswith(".py") and comando != "INFOR.txt"]
    
    comandos_detectados = re.findall(r"\$%([a-zA-Z0-9_]+)%\$", texto)
    for comando in comandos_detectados:
        if comando in comandos:
            print(f"Executando comando interno: {comando}")
            subprocess.Popen(["python", os.path.join(FILE_COMANDOS, f"{comando}.py")])

def chamar_comandos():
    """Retorna os comandos disponíveis no diretório de comandos."""
    return [comando.split(".")[0] for comando in os.listdir(FILE_COMANDOS) if comando.endswith(".py")]

def fala_gemini(texto):
    """Converte texto em fala usando pyttsx3."""
    engine = pyttsx3.init()
    engine.setProperty('rate', 150)
    engine.setProperty('volume', 1)

    def speak():
        engine.say(texto)
        engine.runAndWait()

    # Coloca a função de fala na fila
    fala_fila.put(speak)

    # Se o processamento da fila ainda não está ativo, inicie-o
    if not any(thread.name == "FalaProcessor" for thread in threading.enumerate()):
        threading.Thread(target=processar_fala, name="FalaProcessor", daemon=True).start()


def processar_fala():
    """Processa as falas da fila, uma por vez."""
    while True:
        speak_func = fala_fila.get()  # Obtém a função de fala da fila
        if speak_func is None:
            break  # Se a função for None, significa que o loop de fala deve ser encerrado
        speak_func()

def ativar_audio():
    """Captura áudio e tenta reconhecer a fala."""
    global audio_ativo
    audio_ativo = True
    r = sr.Recognizer()

    while audio_ativo:
        with sr.Microphone() as source:
            print("Gravando... Fale algo.")
            try:
                audio = r.listen(source, timeout=10)
                texto = r.recognize_google(audio, language="pt-BR")
                print(f"Texto reconhecido: {texto}")
                
                gemini = GEMINI()
                comandos = chamar_comandos()
                texto_comando = f"Caso solicitado pode usar comandos internos exemplo: '$%texte%$'. A lista de comandos internos é: {comandos}. Responda: {texto}"
                resposta = gemini.enviar(texto_comando)

                print(f"Resposta: {texto_comando}")
                print(f"Resposta: {resposta}")
                filtro_comando(resposta)
                if resposta:
                    resposta = resposta.replace("$%", "").replace("%$", "")
                
                # Coloca a fala na fila para ser processada
                fala_gemini(resposta)
                
                # Espera um pouco antes de permitir nova ativação do áudio
                time.sleep(1)
                audio_ativo = False

            except sr.WaitTimeoutError:
                print("Nenhum som detectado. Tempo limite esgotado.")
            except sr.UnknownValueError:
                print("Não foi possível entender o áudio.")
            except sr.RequestError as e:
                print(f"Erro ao acessar o serviço de reconhecimento: {e}")
            except KeyboardInterrupt:
                print("Encerrando a detecção de áudio.")
                audio_ativo = False
                break

def desativar_audio():
    """Desativa o reconhecimento de áudio."""
    global audio_ativo
    audio_ativo = False
    print("Áudio desativado.")

def sair(icon, item):
    """Sair quando o item for clicado."""
    global audio_ativo
    print("Saindo...")
    audio_ativo = False  # Sinaliza para parar o reconhecimento de áudio
    fala_fila.put(None)  # Finaliza o processamento da fila
    icon.stop()
    sys.exit()


def on_activate_fala(icon, item):
    """Ativa o reconhecimento de fala."""
    ativar_audio()

def informacoes(icon, item):
    """Exibe informações sobre o programa."""
    INFOR = """Instruções de uso:
    - Ctrl + Alt + A: Ativa o reconhecimento de áudio.
    - Ctrl + Alt + Z: Interrompe a fala do programa.
    """
    file_path = os.path.join(BASE_DIR, "informacoes.txt")
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(INFOR)
    
    if os.name == 'nt':
        os.startfile(file_path)
    else:
        subprocess.run(['xdg-open', file_path])


class SistemaAssistente:
    def __init__(self):
        self.icon = None

    def criar_tray_icon(self):
        """Cria e gerencia o ícone da bandeja."""
        icon_image = cria_imagem()
        self.icon = pystray.Icon("GEMINI Assistant", icon_image, menu=(
            item("Ativar Fala", on_activate_fala),
            item("Informações", informacoes),
            item("Parar fala", desativar_audio),
            item("Sair", sair),
        ))
        self.icon.run()

    def iniciar_reconhecimento_audio(self):
        """Inicia o processo de reconhecimento de áudio e bandeja."""
        if not any(thread.name == "FalaProcessor" for thread in threading.enumerate()):
            threading.Thread(target=processar_fala, name="FalaProcessor", daemon=True).start()

        if not any(thread.name == "TrayIconThread" for thread in threading.enumerate()):
            threading.Thread(target=self.criar_tray_icon, name="TrayIconThread", daemon=True).start()

    def loop_principal(self):
        """Loop principal para controle de ativação do áudio"""
        print("Aperte 'Ctrl + Alt + A' para ativar o reconhecimento de áudio.")
        while True:
            if keyboard.is_pressed('ctrl+alt+a') and not audio_ativo:
                ativar_audio()  # Começa o áudio
                time.sleep(1)  # Evita múltiplas ativações

def main():
    """Função principal que mantém o código do main intacto"""
    ocultar_console()  # Oculta a janela do console
    sistema = SistemaAssistente()
    sistema.iniciar_reconhecimento_audio()
    sistema.loop_principal()

if __name__ == '__main__':
    main()
