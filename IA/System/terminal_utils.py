import subprocess


def execute_command(cmd: str) -> str:
    """Executa o comando e retorna a saída (stdout + stderr formatado)."""
    completed = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    terminal_output = ""
    if completed.stdout and completed.stdout.strip():
        out = completed.stdout.strip()
        print(out)
        terminal_output += out
    if completed.stderr and completed.stderr.strip():
        err = completed.stderr.strip()
        print("Erro:", err)
        if terminal_output:
            terminal_output += "\n"
        terminal_output += "Error: " + err
    return terminal_output
