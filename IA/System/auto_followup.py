import re
from typing import Callable


def handle_terminal_followup(
    ia_instance,
    original_prompt: str,
    cmd: str,
    terminal_output: str,
    execute_command_func: Callable[[str], str],
    comando_bloqueado_func: Callable[[str], bool],
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
        if not new_cmds:
            # IA reafirmou ou não pediu mais ações -> parar
            break

        any_output = False
        for ncmd in new_cmds:
            if comando_bloqueado_func(ncmd):
                print(f"Comando bloqueado por segurança (auto): {ncmd}")
                continue
            print("Executando (auto) comando:", ncmd)
            new_output = execute_command_func(ncmd)
            # salva memória da execução automática
            try:
                ia_instance.memories.adicionar_memoria(followup_prompt, full_text, terminal_output=new_output, command=ncmd)
            except Exception:
                pass

            if new_output.strip():
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
