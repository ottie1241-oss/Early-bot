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

OUTPUT_FILE = "session_output.txt"

try:
    with TelegramClient(StringSession(), API_ID, API_HASH) as client:
        session_string = client.session.save()

        # Save to a file (backup)
        with open(OUTPUT_FILE, "w") as f:
            f.write(session_string)

        # Send it to your own "Saved Messages" in Telegram — easiest way to
        # copy it on mobile, since the Telegram app copies text normally.
        client.send_message("me", f"Your SESSION_STRING:\n\n{session_string}")

        print("\nDONE. Check your Telegram 'Saved Messages' — the session string was sent there.\n")
except Exception as e:
    with open(OUTPUT_FILE, "w") as f:
        f.write(f"ERROR: {e}")
    print(f"\nSomething went wrong. Error written to {OUTPUT_FILE} — open that file to see it.\n")
