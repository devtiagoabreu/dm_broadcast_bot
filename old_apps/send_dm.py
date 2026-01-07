import os
import time
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from dotenv import load_dotenv

load_dotenv()

client = WebClient(token=os.getenv("SLACK_BOT_TOKEN"))

MENSAGEM = """
Olá! 👋
Essa é uma mensagem enviada individualmente.
Qualquer dúvida, estou à disposição.
"""

def enviar_dms():
    try:
        usuarios = client.users_list()["members"]

        for user in usuarios:
            if user["is_bot"] or user["deleted"]:
                continue

            try:
                dm = client.conversations_open(users=user["id"])
                client.chat_postMessage(
                    channel=dm["channel"]["id"],
                    text=MENSAGEM
                )

                print(f"Mensagem enviada para {user['profile']['real_name']}")
                time.sleep(1.2)  # anti-spam

            except SlackApiError as e:
                print(f"Erro ao enviar para {user['id']}: {e.response['error']}")

    except SlackApiError as e:
        print("Erro geral:", e.response["error"])

if __name__ == "__main__":
    enviar_dms()
