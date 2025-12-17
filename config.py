from dotenv import load_dotenv
import os

# Carrega variáveis de ambiente (se existir .env)
load_dotenv()

# Parâmetros de runtime (podem ser sobrescritos via .env)
MODEL = os.getenv("MODEL", "ministral-3:3b")
TEMPERATURE = float(os.getenv("TEMPERATURE", "0.3"))
MAX_AUTOCALLS = int(os.getenv("MAX_AUTOCALLS", "10"))

# Instância compartilhada do filtro de comandos
from IA.System.Comandos.Filtro import Filtro
FILTRO = Filtro()

# Padrão para detecção de imagens em prompts
IMAGE_PATTERN = r"([^\s]+?\.(?:png|jpe?g|webp|gif|bmp|tiff))"

# Export: nomes esperados pelo main.py
__all__ = ["MODEL", "TEMPERATURE", "MAX_AUTOCALLS", "FILTRO", "IMAGE_PATTERN"]
