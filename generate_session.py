"""
RUN THIS ONCE ON REPLIT OR GITHUB CODESPACES — NOT ON RENDER.

This logs in interactively with the alt Telegram account (the one that is
a member of https://t.me/earlymemeacces) and prints a SESSION_STRING.

Steps:
1. pip install telethon
2. Fill in API_ID and API_HASH below (from my.telegram.org, for the alt account)
3. Run: python generate_session.py
4. It will ask for the alt account's phone number, then a login code sent
   to that account's Telegram app. Enter both when prompted.
5. Copy the long string it prints at the end. That is your SESSION_STRING.
   Save it somewhere safe — you'll paste it as an env var on Render.
   Do NOT share it or commit it anywhere. It's equivalent to a login token
   for that account.
"""

from telethon.sync import TelegramClient
from telethon.sessions import StringSession

API_ID = 39801320
API_HASH = "9efb94b33a2442c3d50302f4b1bc9313"

with TelegramClient(StringSession(), API_ID, API_HASH) as client:
    print("\n\n=== YOUR SESSION STRING (copy everything below) ===\n")
    print(client.session.save())
    print("\n=== END SESSION STRING ===\n\n")
