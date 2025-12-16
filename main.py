import IA.System.Conn as IA
import IA.System.Comandos.Filtro as Filtro
import subprocess
import os
from dotenv import load_dotenv
import re

load_dotenv()

model = os.getenv("MODEL", "ministral-3:3b")
temperature = float(os.getenv("TEMPERATURE", "0.3"))

filtro = Filtro.Filtro()


FORBIDDEN_PATTERNS = [
    "reboot",
    "shutdown",
    "poweroff",
    "halt",
    "rm -rf /",
    "rm -rf /*",
]


def comando_bloqueado(cmd: str) -> bool:
    """Retorna True se o comando contiver padrões perigosos."""
    cmd_lower = cmd.lower()
    for pattern in FORBIDDEN_PATTERNS:
        if pattern in cmd_lower:
            return True
    return False

def main():
    ia_instance = IA.IA(model=model, temperature=temperature)
    while True:
        user_input = input("You: ")
        if user_input.lower() in ['exit', 'quit']:
            print("Ate logo!")
            break
        
        # Streaming em tempo real
        print("IA:", end=" ", flush=True)
        response = ""
        for chunk in ia_instance.generate_response_stream(user_input):
            print(chunk, end="", flush=True)
            response += chunk
        print()  # Nova linha após a resposta completa
        
        comandos_encontrados = filtro.Filtro_texto_IA(response)

        # Detecta e executa comandos do formato [Terminal:["COMANDO_COMPLETO"]]
        # Ex.: [Terminal:["ls -l Documentos"]]
        # O regex já captura apenas o conteúdo entre aspas (inclusive comandos multilinha).
        terminal_cmds = re.findall(r'\[Terminal:\["(.*?)"\]\]', response, re.DOTALL)
        for cmd in terminal_cmds:
            # Verifica se o comando é seguro antes de executar
            if comando_bloqueado(cmd):
                print(f"Comando bloqueado por segurança (main.py): {cmd}")
                continue
            # Executa usando shell=True para suportar comandos complexos (heredoc, pipes, etc)
            try:
                print("Executando comando:", cmd)
                completed = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                if completed.stdout and completed.stdout.strip():
                    print(completed.stdout.strip())
                if completed.stderr and completed.stderr.strip():
                    print("Erro:", completed.stderr.strip())
            except Exception as e:
                print("Falha ao executar comando:", e)

if __name__ == "__main__":
    main()