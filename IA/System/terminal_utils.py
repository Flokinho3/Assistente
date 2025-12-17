import datetime
import os
import shutil
import subprocess
import re


def _build_screenshot_path():
    base_dir = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "Persona", "screenshots"))
    os.makedirs(base_dir, exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    return os.path.join(base_dir, f"screenshot-{timestamp}.png")


def capture_screenshot():
    """Tira um print do desktop usando o primeiro utilitário disponível."""
    output_path = _build_screenshot_path()
    candidates = [
        ("gnome-screenshot", lambda bin_path: [bin_path, "-f", output_path]),
        ("spectacle", lambda bin_path: [bin_path, "-b", "-n", "-o", output_path]),
        ("scrot", lambda bin_path: [bin_path, output_path]),
        ("import", lambda bin_path: [bin_path, "-window", "root", output_path]),
    ]

    last_error = None
    for binary, cmd_builder in candidates:
        bin_path = shutil.which(binary)
        if not bin_path:
            continue

        # Alguns utilitários (ex: 'import') aceitam variações de argumentos;
        # tente múltiplas formas para aumentar robustez.
        cmds_to_try = []
        primary = cmd_builder(bin_path)
        cmds_to_try.append(primary)
        if binary == "import":
            # também tente apenas: import <filename>
            cmds_to_try.append([bin_path, output_path])

        for cmd in cmds_to_try:
            try:
                result = subprocess.run(cmd, capture_output=True, text=True)
            except Exception as e:
                last_error = str(e)
                continue

            if result.returncode == 0 and os.path.exists(output_path):
                return output_path, None

            stdout = (result.stdout or "").strip()
            stderr = (result.stderr or "").strip()
            combined = "\n".join([s for s in (stdout, stderr) if s])
            last_error = combined or f"Falha ao executar {binary} (exit {result.returncode})"

    if last_error:
        return None, last_error

    return None, "Nenhum utilitário de captura encontrado (gnome-screenshot, spectacle, scrot ou import)."


def is_screenshot_command(cmd: str) -> bool:
    normalized = cmd.strip().lower()
    return normalized in {"screenshot", "printscreen", "captura_tela", "capturar_tela", "take_screenshot"}


def execute_command(cmd: str) -> str:
    """Executa o comando e retorna a saída (stdout + stderr formatado)."""
    # Suporte a comando customizado não-interativo para escrita de arquivos:
    # Exemplo que o modelo pode usar:
    # writefile /caminho/para/arquivo << 'TAG'\nconteúdo...\nTAG
    writefile_re = re.compile(
        r"writefile\s+(?P<file>\S+)\s*<<\s*'(?P<tag>[^']+)'\n(?P<content>.*?)\n(?P=tag)\s*$",
        re.DOTALL,
    )
    m = writefile_re.search(cmd)
    if m:
        filename = os.path.expanduser(m.group('file'))
        content = m.group('content')
        try:
            os.makedirs(os.path.dirname(filename), exist_ok=True) if os.path.dirname(filename) else None
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)
            msg = f"Arquivo criado/atualizado: {filename}"
            print(msg)
            return msg
        except Exception as e:
            err = str(e)
            print("Erro:", err)
            return "Error: " + err

    # Detecta um heredoc do tipo: cat << 'TAG' > filename\n...content...\nTAG
    heredoc_re = re.compile(r"cat\s+<<\s*'(?P<tag>[^']+)'\s*>\s*(?P<file>\S+)\n(?P<content>.*?)\n(?P=tag)\s*$", re.DOTALL)
    m = heredoc_re.search(cmd)
    if m:
        filename = os.path.expanduser(m.group('file'))
        content = m.group('content')
        try:
            os.makedirs(os.path.dirname(filename), exist_ok=True) if os.path.dirname(filename) else None
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)
            msg = f"Arquivo criado: {filename}"
            print(msg)
            return msg
        except Exception as e:
            err = str(e)
            print("Erro:", err)
            return "Error: " + err

    # Fallback: execute via shell
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
