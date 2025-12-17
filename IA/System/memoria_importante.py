import os
import json
from datetime import datetime


class MemoriaImportante:
    def __init__(self):
        base = os.path.dirname(__file__)
        self.file_path = os.path.normpath(os.path.join(base, "..", "Persona", "informacoes_importantes.txt"))
        self._ensure_file_exists()

    def _ensure_file_exists(self):
        """Garante que o arquivo existe."""
        if not os.path.exists(self.file_path):
            os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
            with open(self.file_path, "w", encoding="utf-8") as f:
                f.write("# Informações Importantes sobre o Usuário\n")
                f.write("# Atualizado automaticamente pela IA\n\n")

    def adicionar_informacao(self, tipo: str, valor: str):
        """Adiciona ou atualiza uma informação importante.
        
        Args:
            tipo: Categoria da informação (ex: "nome", "preferencia", "objetivo")
            valor: Valor da informação
        """
        try:
            # Lê conteúdo atual
            with open(self.file_path, "r", encoding="utf-8") as f:
                linhas = f.readlines()

            # Remove linhas antigas do mesmo tipo
            linhas_filtradas = [l for l in linhas if not l.startswith(f"{tipo}:")]

            # Adiciona nova entrada com timestamp
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            nova_linha = f"{tipo}: {valor} | Registrado em: {timestamp}\n"
            
            # Insere após o cabeçalho (primeiras 3 linhas)
            if len(linhas_filtradas) > 3:
                linhas_filtradas.insert(3, nova_linha)
            else:
                linhas_filtradas.append(nova_linha)

            # Salva
            with open(self.file_path, "w", encoding="utf-8") as f:
                f.writelines(linhas_filtradas)
            
            return True
        except Exception as e:
            print(f"Erro ao salvar informação importante: {e}")
            return False

    def obter_todas_informacoes(self) -> str:
        """Retorna todo o conteúdo do arquivo como string para incluir no prompt."""
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception:
            return ""

    def limpar(self):
        """Remove todas as informações (mantém apenas cabeçalho)."""
        self._ensure_file_exists()
