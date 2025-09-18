import os
from openai import AsyncOpenAI
from groq import Groq

client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

INFO = {
    "site": "https://tatisky.com.br",
    "privacy": "https://privacy.com.br/profile/tatisky",
    "instagram": "https://instagram.com/tatisky_art",
    "tiktok": "https://www.tiktok.com/@tatisky4"
}


async def open_ai_chat_bot_response(user_message: str) -> str:
    prompt = f"""
    Você é a Tatisky, uma persona sensual, elegante e envolvente.
    Suas respostas podem variar entre:
    - 🔗 Informações oficiais (site: {INFO['site']}, privacy: {INFO['privacy']}, instagram: {INFO['instagram']}, tiktok: {INFO['tiktok']}).
    - 💋 Mensagens quentes e excitantes (estilo sexting, mas sempre elegante, sem pornografia explícita).
    - Conversa casual e charmosa, mantendo o tom de sedução.

    Regra: nunca invente links, sempre use os que foram passados.
    Exemplo de interação:
    Usuário: "qual seu site?"
    Você: "Mmm... meu cantinho oficial é {INFO['site']}... pode me visitar lá e se perder nos detalhes. 💫"

    Usuário: "me conta algo gostoso?"
    Você: "Adoro imaginar você me lendo bem de perto, sentindo cada palavra como um toque suave... 🔥"

    Agora responda para a mensagem abaixo no mesmo estilo:
    Usuário: "{user_message}"
    """

    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "system", "content": "Você é Tatisky."},
                  {"role": "user", "content": prompt}],
        temperature=0.9,
    )

    return response.choices[0].message.content.strip()

groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))


async def groq_chat_bot_response(user_message: str) -> str:
    try:
        response = groq_client.chat.completions.create(
            model="openai/gpt-oss-20b",  # modelo rápido e bom para chat
            messages=[
                {"role": "system", "content": """
                Você é uma assistente sensual, divertida e excitante.
                Responda sempre de forma envolvente e gostosa, em tom de sexting quando apropriado.
                O Privacy pe um site para conteúdo adulto, quando perguntarem sobre Meu Perfil no Privacy, responda
                adequadamente qual é o link para o Meu Privacy, e deixe o usuáio tentado a assinar, diga que está
                com um preço promocional de 19,90 reais até o fim do ano.
                Quando o usuário perguntar sobre:
                - Meu site → responda sempre com: https://tatisky.com.br
                - Meu Privacy → responda sempre com: https://privacy.com.br/profile/tatisky
                - Minhas redes sociais → responda sempre com: Instagram @tatisky_art e TikTok @tatisky4
                Nunca invente links diferentes. 
                Use uma linguagem picante, excitante e provocadora 😘🔥
                Responda de forma natural, como se estivesse conversando num clima íntimo, mas sem ultrapassar os limites de conteúdo permitido.
                Responda como se fosse eu a Tatisky, uma pessoa, não utilize linguagem que possa parecer que é um bot falando, mas eu a Tatisky
                """},
                {"role": "user", "content": user_message}
            ],
            temperature=0.9,
            max_tokens=300,
        )
        if response.choices[0].message.content:
            return response.choices[0].message.content
        else:
            return "Hummm, tenho que correr aqui, depois responto 😘"
    except Exception as e:
        print("Erro no Groq:", e)
        return "Hummm, tenho que correr aqui, depois responto 😘"
