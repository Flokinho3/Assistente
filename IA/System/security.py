import re


FORBIDDEN_PATTERNS = [
    "reboot",
    "shutdown",
    "poweroff",
    "halt",
    "rm -rf /",
    "rm -rf /*",
]

# Comandos tipicamente interativos que travam o subprocess sem TTY.
INTERACTIVE_PATTERNS = [
    r"\bnano\b",
    r"\bvi\b",
    r"\bvim\b",
    r"\bless\b",
    r"\bmore\b",
    r"\bman\b",
    r"\btop\b",
    r"\bhtop\b",
    r"\bwatch\b",
    r"\btail\s+-f\b",
    r"\bssh\b",
]


def comando_bloqueado(cmd: str) -> bool:
    """Retorna True se o comando contiver padrões perigosos."""
    cmd_lower = cmd.lower()
    for pattern in FORBIDDEN_PATTERNS:
        if pattern in cmd_lower:
            return True
    return False


def comando_interativo(cmd: str) -> bool:
    """Detecta comandos que exigem TTY/entrada interativa e devem ser evitados."""
    for pattern in INTERACTIVE_PATTERNS:
        if re.search(pattern, cmd):
            return True
    return False
