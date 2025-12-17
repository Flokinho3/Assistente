from dotenv import load_dotenv
# Carrega .env ANTES de importar config
load_dotenv()

import IA.System.Conn as IA
import os
import re
from IA.System.auto_followup import handle_terminal_followup
from IA.System.security import comando_bloqueado, comando_interativo
from IA.System.terminal_utils import capture_screenshot, execute_command, is_screenshot_command
from config import MODEL, TEMPERATURE, MAX_AUTOCALLS, FILTRO, IMAGE_PATTERN


def _normalize_image_path(raw_path: str) -> str:
    expanded = os.path.expanduser(raw_path)
    if not os.path.isabs(expanded):
        expanded = os.path.abspath(expanded)
    return expanded


def extract_images_and_prompt(text: str):
    matches = re.findall(IMAGE_PATTERN, text, flags=re.IGNORECASE)
    found_images = []
    missing_images = []
    for raw in matches:
        normalized = _normalize_image_path(raw)
        if os.path.exists(normalized):
            found_images.append(normalized)
        else:
            missing_images.append(raw)

    cleaned_text = text
    for raw in matches:
        cleaned_text = cleaned_text.replace(raw, " ")
    cleaned_text = re.sub(r"\s+", " ", cleaned_text).strip()

    notes = []
    if found_images:
        notes.append(f"imagens anexadas: {', '.join(os.path.basename(p) for p in found_images)}")
    if missing_images:
        notes.append(f"imagens não encontradas: {', '.join(missing_images)}")

    if notes:
        note_text = " | ".join(notes)
        cleaned_text = f"{cleaned_text}\n[{note_text}]" if cleaned_text else f"[{note_text}]"

    return cleaned_text if cleaned_text else text, found_images, missing_images

def main():
    ia_instance = IA.IA(model=MODEL, temperature=TEMPERATURE)
    print(f"Modelo carregado: {MODEL} | Temperatura: {TEMPERATURE}")
    try:
        while True:
            try:
                user_input = input("You: ")
            except KeyboardInterrupt:
                print("\nInterrompido pelo usuário. Saindo.")
                break
            if user_input.lower() in ['exit', 'quit']:
                print("Ate logo!")
                break

            prompt_text, images, missing_images = extract_images_and_prompt(user_input)
            if missing_images:
                print(f"Imagens não encontradas: {', '.join(missing_images)}")

            # Streaming em tempo real
            print("IA:", end=" ", flush=True)
            response = ""
            try:
                for chunk in ia_instance.generate_response_stream(prompt_text, images=images):
                    print(chunk, end="", flush=True)
                    response += chunk
            except KeyboardInterrupt:
                print("\nInterrompido pelo usuário durante a resposta. Saindo.")
                return
            print()  # Nova linha após a resposta completa

            comandos_encontrados = FILTRO.Filtro_texto_IA(response)

            # Detecta e salva informações importantes [Memoria:"tipo = valor"]
            memoria_cmds = re.findall(r'\[Memoria:"([^"]+)"\]', response)
            for memo in memoria_cmds:
                if "=" in memo:
                    try:
                        tipo, valor = memo.split("=", 1)
                        tipo = tipo.strip()
                        valor = valor.strip()
                        try:
                            ia_instance.memories.adicionar_memoria(tipo, valor)
                            print(f"ℹ️  Informação salva: {tipo} = {valor}")
                        except Exception:
                            pass
                    except Exception as e:
                        print(f"Erro ao processar [Memoria]: {e}")

            # Detecta e executa comandos do formato [Terminal:["COMANDO_COMPLETO"]]
            terminal_cmds = re.findall(r'\[Terminal:\["(.*?)"\]\]', response, re.DOTALL)
            for cmd in terminal_cmds:
                if comando_bloqueado(cmd):
                    print(f"Comando bloqueado por segurança (main.py): {cmd}")
                    continue

                if comando_interativo(cmd):
                    print(f"Comando interativo detectado e bloqueado (use heredoc para editar arquivos): {cmd}")
                    continue

                if is_screenshot_command(cmd):
                    screenshot_path, error = capture_screenshot()
                    if error:
                        print(f"Falha ao capturar screenshot: {error}")
                        continue

                    print(f"Screenshot salva em: {screenshot_path}")
                    filename = os.path.basename(screenshot_path) if screenshot_path is not None else "imagem"
                    analysis_prompt = (
                        f"Foi capturada uma captura de tela a pedido do modelo ({cmd}). "
                        f"Analise o que aparece na imagem {filename} e descreva brevemente."
                    )

                    print("IA (screenshot):", end=" ", flush=True)
                    followup_response = ""
                    images_arg = [screenshot_path] if screenshot_path is not None else None
                    for chunk in ia_instance.generate_response_stream(analysis_prompt, images=images_arg):
                        print(chunk, end="", flush=True)
                        followup_response += chunk
                    print()

                    try:
                        ia_instance.memories.adicionar_memoria(analysis_prompt, followup_response, command=cmd, terminal_output=screenshot_path)
                    except Exception:
                        pass
                    continue
                try:
                    print("Executando comando:", cmd)
                    terminal_output = execute_command(cmd)

                    try:
                        ia_instance.memories.adicionar_memoria(user_input, response, terminal_output=terminal_output, command=cmd)
                    except Exception as e:
                        print("Falha ao salvar memória da execução:", e)

                    if terminal_output.strip():
                        handle_terminal_followup(
                            ia_instance,
                            user_input,
                            cmd,
                            terminal_output,
                            execute_command,
                            comando_bloqueado,
                            comando_interativo,
                            max_autocalls=MAX_AUTOCALLS,
                        )
                except Exception as e:
                    print("Falha ao executar comando:", e)
                    try:
                        ia_instance.memories.adicionar_memoria(user_input, response, terminal_output=str(e), command=cmd)
                    except Exception:
                        pass
    except KeyboardInterrupt:
        print("\n\nInterrompido. Até logo!")

if __name__ == "__main__":
    main()
