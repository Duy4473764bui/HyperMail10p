import discord
import requests
import asyncio
import re
import time
import os

TOKEN = os.getenv("TOKEN")

intents = discord.Intents.default()
intents.message_content = True  # 🔥 QUAN TRỌNG

client = discord.Client(intents=intents)

user_data = {}

# tạo mail
def create_mail():
    domain = requests.get("https://api.mail.tm/domains").json()["hydra:member"][0]["domain"]
    email = f"user{int(time.time())}@{domain}"
    password = "12345678"

    requests.post("https://api.mail.tm/accounts", json={
        "address": email,
        "password": password
    })

    token = requests.post("https://api.mail.tm/token", json={
        "address": email,
        "password": password
    }).json()["token"]

    return email, token

# check OTP loop
async def check_otp(user_id, channel, token):
    headers = {"Authorization": f"Bearer {token}"}

    while True:
        try:
            res = requests.get("https://api.mail.tm/messages", headers=headers).json()

            if res["hydra:member"]:
                msg_id = res["hydra:member"][0]["id"]
                msg = requests.get(f"https://api.mail.tm/messages/{msg_id}", headers=headers).json()

                text = msg["text"]
                otp = re.search(r"\d{4,6}", text)

                if otp:
                    await channel.send(f" OTP của <@{user_id}>: `{otp.group()}`")
                    return

            await asyncio.sleep(2)

        except:
            await asyncio.sleep(3)

@client.event
async def on_ready():
    print(f"Bot online: {client.user}")

@client.event
async def on_message(message):
    if message.author.bot:
        return

    if message.content == "!mail":
        email, token = create_mail()

        user_data[message.author.id] = token

        await message.channel.send(f"📩 Mail của m: `{email}`\n⏳ Đang chờ OTP...")

        # chạy nền check OTP
        asyncio.create_task(check_otp(message.author.id, message.channel, token))

client.run(TOKEN)
