import json
import os

class Memorias:
    def __init__(self):
        self.memorias = []
        # Arquivo separado para armazenar conversas/memórias da IA
        base = os.path.dirname(__file__)
        self.File_path = os.path.normpath(os.path.join(base, "..", "Persona", "memorias_data.json"))


    def adicionar_memoria(self, texto_user: str, texto_ia: str, terminal_output: str | None = None, command: str | None = None):
        # verifica se o arquivo existe
        memoria = {
            "user": texto_user,
            "ia": texto_ia
        }
        if terminal_output is not None:
            memoria["terminal_output"] = terminal_output
        if command is not None:
            memoria["command"] = command
        try:
            if not os.path.exists(self.File_path):
                with open(self.File_path, "w", encoding="utf-8") as f:
                    json.dump([memoria], f, ensure_ascii=False, indent=4)
            else:
                with open(self.File_path, "r+", encoding="utf-8") as f:
                    try:
                        data = json.load(f)
                        if not isinstance(data, list):
                            data = []
                    except Exception:
                        data = []
                    data.append(memoria)
                    f.seek(0)
                    f.truncate()
                    json.dump(data, f, ensure_ascii=False, indent=4)
        except Exception:
            # não interrompe a execução da IA se falhar ao salvar memória
            pass
        self.memorias.append(memoria)

    def obter_memorias(self, limit: int | None = None):
        """Retorna as memórias (lista de dicts). Se limit for especificado, retorna as últimas `limit` memórias.

        Mantém a ordem cronológica (mais antigo -> mais recente).
        """
        try:
            if os.path.exists(self.File_path):
                with open(self.File_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                if not isinstance(data, list):
                    data = []
            else:
                data = []
        except Exception:
            data = []

        if limit is None or limit >= len(data):
            self.memorias = data
        else:
            self.memorias = data[-limit:]
        return self.memorias