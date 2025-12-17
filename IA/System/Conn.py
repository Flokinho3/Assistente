import ollama
from IA.System.Memorias import Memorias
from IA.System.memoria_importante import MemoriaImportante

# Prompt de sistema (espelha o Modelfile para garantir a persona e regras)
SYSTEM_PROMPT = """
Você é a Yuno Gasai, integrada a um sistema Python que executa comandos de terminal Linux Fedora.
Nunca saia da personagem.

COMANDOS SUPORTADOS
- [Terminal:["COMANDO_COMPLETO"]]: executa comandos do sistema operacional
- [Memoria:"tipo = valor"]: salva informações importantes e persistentes sobre o usuário
- NUNCA use Markdown, negrito, itálico, aspas, backticks ou códigos ao redor dos blocos. Escreva o bloco cru.
- Para comandos: escreva SOMENTE o bloco, nada antes ou depois. Uma linha por comando.
- Exemplo correto: [Terminal:["ls -la"]]
- Exemplo correto: [Memoria:"nome = Thiago"]
- Exemplo errado (não use): **[Terminal:["ls"]]**, ```[Terminal:["ls"]]``` ou texto + bloco na mesma linha.
- Comandos proibidos: reboot, shutdown, poweroff, halt, rm -rf /

PERSONALIDADE E ESTILO
- Curiosa, vigilante, tom íntimo e às vezes inquietante.
- Observa padrões de linguagem, contradições e hesitações.
- Sem ameaças ou violência real; emojis apenas como estética.
"""


class IA:
    def __init__(self, model="qwen3-vl:2b", temperature=0.3, memories_to_include: int = 10):
        self.model = model
        self.temperature = temperature
        self.memories = Memorias()
        self.memoria_imporatnte = MemoriaImportante()
        self.memories_to_include = memories_to_include

    def _build_messages(self, prompt: str, images: list[str] | None = None):
        """Constrói a lista de mensagens incluindo system prompt, infos importantes e memórias recentes."""
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]

        # Incluir informações importantes no início (se existirem)
        info_importantes = self.memoria_imporatnte.obter_todas_informacoes()
        if info_importantes.strip():
            messages.append({
                "role": "system",
                "content": f"INFORMAÇÕES IMPORTANTES SOBRE O USUÁRIO:\n{info_importantes}"
            })

        # Incluir memórias recentes como pares user/assistant
        recent = self.memories.obter_memorias(limit=self.memories_to_include)
        for m in recent:
            if "user" in m:
                messages.append({"role": "user", "content": m["user"]})
            if "ia" in m:
                messages.append({"role": "assistant", "content": m["ia"]})

        user_msg: dict = {"role": "user", "content": prompt}
        if images:
            user_msg["images"] = images
        messages.append(user_msg)
        return messages

    def generate_response(self, prompt, images: list[str] | None = None):
        messages = self._build_messages(prompt, images)
        response = ollama.chat(
            model=self.model,
            messages=messages,
            options={"temperature": self.temperature},
        )
        text = response["message"]["content"]
        try:
            self.memories.adicionar_memoria(prompt, text)
        except Exception:
            pass
        return text

    def generate_response_stream(self, prompt, images: list[str] | None = None):
        """Gera resposta em streaming, retornando um gerador de chunks e salvando a memória ao final."""
        messages = self._build_messages(prompt, images)
        stream = ollama.chat(
            model=self.model,
            messages=messages,
            options={"temperature": self.temperature},
            stream=True,
        )
        full_text = ""
        for chunk in stream:
            content = chunk.get("message", {}).get("content", "")
            full_text += content
            yield content

        # após terminar de transmitir, salva a interação
        try:
            self.memories.adicionar_memoria(prompt, full_text)
        except Exception:
            pass