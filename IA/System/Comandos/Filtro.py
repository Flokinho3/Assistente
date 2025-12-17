import os
import re
import subprocess


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


class Filtro:
    def __init__(self):
        # Mantemos a classe simples: apenas filtra padrões e bloqueia perigosos.
        pass

    def Filtro_texto_IA(self, texto):
        """Extrai blocos de comando do formato [Terminal:["COMANDO_COMPLETO"]].

        - Não há whitelist: qualquer comando é retornado, apenas bloqueamos padrões perigosos.
        - Retorna lista de dicts: [{"Terminal": ["cmd1", "cmd2", ...]}]
        """
        comandos_encontrados = []
        pattern = r'\[(\w+):\["(.*?)"\]\]'
        matches = re.findall(pattern, texto, re.DOTALL)
        for nome_comando, cmd_str in matches:
            if nome_comando.lower() == "terminal":
                comandos_encontrados.append({"Terminal": [cmd_str]})
        return comandos_encontrados
       
    def executar_comandos(self, comandos_encontrados):
        """Executa os comandos encontrados no terminal"""
        for comando_dict in comandos_encontrados:
            for tipo, comandos in comando_dict.items():
                if tipo == "Terminal":
                    for comando in comandos:
                        # Verifica se o comando é seguro antes de executar
                        if comando_bloqueado(comando):
                            print(f"[Comando bloqueado por segurança (Filtro.py): {comando}]")
                            continue
                        try:
                            print(f"\n[Executando comando: {comando}]")
                            resultado = subprocess.run(
                                comando,
                                shell=True,
                                capture_output=True,
                                text=True,
                                timeout=30
                            )
                            if resultado.stdout:
                                print(f"Saída:\n{resultado.stdout}")
                            if resultado.stderr:
                                print(f"Erro:\n{resultado.stderr}")
                            print(f"[Comando finalizado com código: {resultado.returncode}]")
                        except subprocess.TimeoutExpired:
                            print(f"[Erro: Comando '{comando}' excedeu o tempo limite]")
                        except Exception as e:
                            print(f"[Erro ao executar comando '{comando}': {e}]")