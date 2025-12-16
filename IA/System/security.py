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
