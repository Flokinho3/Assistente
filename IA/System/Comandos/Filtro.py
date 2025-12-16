import os
import json
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
       self.File_Filtro = os.path.join(os.path.dirname(__file__), 'comandos.json')
       self.conteudo_arquivo = self._get_conteudo_arquivo()
   
    def Filtro_texto_IA(self, texto):
       """
       Docstring para Filtro_texto_IA
       Funçao que recebe o texto da IA e procura:
       "[{String_Comando}: ["Parâmetro1", "Parâmetro2", ...]}]"
       caso encontre, retorna uma lista com os comandos e parâmetros encontrados.
       
       :param self: Instância da classe Filtro
       :param texto: Texto retornado pela IA
       """
       comandos_encontrados = []
       # Regex para encontrar padrões como [Terminal:["ls"]]
       pattern = r'\[(\w+):\s*\[([^\]]+)\]\]'
       matches = re.findall(pattern, texto)
       for match in matches:
           nome_comando = match[0]
           params_str = match[1]
           # Parse os parâmetros
           params = [p.strip().strip('"').strip("'") for p in params_str.split(',')]
           # Verifica se o comando existe e se os parâmetros são válidos
           if nome_comando in self.conteudo_arquivo:
               valid_params = self.conteudo_arquivo[nome_comando]
               # Filtra apenas parâmetros válidos
               filtered_params = [p for p in params if p in valid_params]
               if filtered_params:
                   comandos_encontrados.append({nome_comando: filtered_params})
       return comandos_encontrados

    def _get_conteudo_arquivo(self):
       with open(self.File_Filtro, 'r', encoding='utf-8') as file:
           return json.load(file)
       
    def executar_comandos(self,comandos_encontrados):
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