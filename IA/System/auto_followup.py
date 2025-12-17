import re
from typing import Callable

from IA.System.terminal_utils import capture_screenshot, is_screenshot_command


def handle_terminal_followup(
    ia_instance,
    original_prompt: str,
    cmd: str,
    terminal_output: str,
    execute_command_func: Callable[[str], str],
    comando_bloqueado_func: Callable[[str], bool],
    comando_interativo_func: Callable[[str], bool] | None = None,
    max_autocalls: int = 3,
):
    """Auto-invoca a IA enquanto houver saída e até atingir `max_autocalls`.

    Parâmetros:
    - ia_instance: instância da camada de IA (deve oferecer `generate_response_stream` e `memories.adicionar_memoria`).
    - original_prompt: prompt original do usuário.
    - cmd: comando que foi executado originalmente.
    - terminal_output: saída do comando.
    - execute_command_func: função que executa um comando e retorna a saída (stdout+stderr).
    - comando_bloqueado_func: função que verifica se um comando é perigoso.
    - max_autocalls: limite de iterações automáticas para evitar loops.
    """
    if not terminal_output.strip():
        return

    followup_prompt = (
        f"Aqui está a saída do comando `{cmd}`:\n---\n{terminal_output}\n---\n"
        "Se você esperava essa saída, reafirme brevemente o resultado e NÃO gere novos blocos [Terminal]. "
        "Se precisar executar mais comandos para continuar a tarefa, gere somente blocos "
        "[Terminal:[\"...\"]] por linha (um comando por linha). "
        "Lembre-se das regras de segurança."
        f"Voce tem um limite de {max_autocalls} chamadas automáticas para executar comandos adicionais se necessário."
    )
    print(followup_prompt)

    auto_calls = 0
    executed_cmds = set()
    previous_outputs: dict[str, str] = {}
    while auto_calls < max_autocalls:
        print("IA (auto):", end=" ", flush=True)
        full_text = ""
        for chunk in ia_instance.generate_response_stream(followup_prompt):
            print(chunk, end="", flush=True)
            full_text += chunk
        print()

        # salva memória do followup
        try:
            ia_instance.memories.adicionar_memoria(followup_prompt, full_text, terminal_output=terminal_output, command=cmd)
        except Exception:
            pass

        new_cmds = re.findall(r'\[Terminal:\["(.*?)"\]\]', full_text, re.DOTALL)
        # deduplicate preserving order to avoid re-executing the same commands
        dedup_cmds = []
        seen = set()
        for c in new_cmds:
            if c not in seen:
                dedup_cmds.append(c)
                seen.add(c)

        if not dedup_cmds:
            # IA reafirmou ou não pediu mais ações -> parar
            break

        any_output = False
        for ncmd in dedup_cmds:
            if comando_bloqueado_func(ncmd):
                print(f"Comando bloqueado por segurança (auto): {ncmd}")
                continue
            if comando_interativo_func and comando_interativo_func(ncmd):
                print(f"Comando interativo detectado e bloqueado (auto): {ncmd}")
                continue
            if ncmd in executed_cmds:
                print(f"Comando já executado nesta sequência (ignorando): {ncmd}")
                continue
            if is_screenshot_command(ncmd):
                screenshot_path, error = capture_screenshot()
                auto_calls += 1
                if error:
                    print(f"Falha ao capturar screenshot (auto): {error}")
                    continue

                print(f"Screenshot (auto) salva em: {screenshot_path}")
                analysis_prompt = (
                    f"Foi capturada uma captura de tela a pedido do modelo ({ncmd}). "
                    f"Analise com o maximo de detalhes que aparece na imagem {screenshot_path} e descreva, nomes,links,hora...."
                )

                print("IA (screenshot auto):", end=" ", flush=True)
                analysis_response = ""
                for chunk in ia_instance.generate_response_stream(analysis_prompt, images=[screenshot_path]):
                    print(chunk, end="", flush=True)
                    analysis_response += chunk
                print()

                try:
                    ia_instance.memories.adicionar_memoria(analysis_prompt, analysis_response, command=ncmd, terminal_output=screenshot_path)
                except Exception:
                    pass
                return
            print("Executando (auto) comando:", ncmd)
            new_output = execute_command_func(ncmd)
            executed_cmds.add(ncmd)

            # se a saída for idêntica à anterior para este comando, não continuar em loop
            prev = previous_outputs.get(ncmd)
            if prev is not None and prev == new_output:
                print(f"Saída idêntica detectada para {ncmd}, interrompendo reexecução.")
                continue
            previous_outputs[ncmd] = new_output
            # salva memória da execução automática
            try:
                ia_instance.memories.adicionar_memoria(followup_prompt, full_text, terminal_output=new_output, command=ncmd)
            except Exception:
                pass

            if new_output.strip():
                # ignore respostas que são apenas erros repetidos (começam com 'Error:')
                if new_output.strip().startswith("Error:") and prev == new_output:
                    print("Erro repetido detectado, não continuará a sequência automática para este comando.")
                    continue

                any_output = True
                # atualiza followup para nova saída
                followup_prompt = (
                    f"Aqui está a saída do comando `{ncmd}`:\n---\n{new_output}\n---\n"
                    "Se você esperava essa saída, reafirme brevemente o resultado e NÃO gere novos blocos [Terminal]. "
                    "Se precisar executar mais comandos para continuar a tarefa, gere somente blocos "
                    "[Terminal:[\"...\"]] por linha."
                )

            auto_calls += 1
            if auto_calls >= max_autocalls:
                break

        if not any_output:
            # sem saída nova -> não continuar
            break

    if auto_calls >= max_autocalls:
        print("Máximo de auto-chamadas atingido, interrompendo para evitar loops.")
