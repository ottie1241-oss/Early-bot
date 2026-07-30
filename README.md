# Meme Coin + Raider Job Alert Bot

Posts to your channel every 30 minutes:
- Up to 10 newly launched meme coins (ETH, BSC, Solana, Base, Arbitrum, Polygon)
- Any messages in your chosen group that look like raider-job recruitment posts

## Step 1 — Create your posting bot
1. Message @BotFather on Telegram → `/newbot` → follow prompts
2. Copy the token it gives you (this is `BOT_TOKEN`)
3. Add this bot as an **admin** of your channel (`-1003710765715`) so it can post

## Step 2 — Generate the Telethon session string
Do this on Replit or Codespaces (NOT on Render — it needs interactive input):
1. Upload `generate_session.py` to a new Replit project
2. `pip install telethon`
3. Run `python generate_session.py`
4. Enter the **alt account's** phone number, then the login code sent to it
5. Copy the long string it prints — this is `SESSION_STRING`
6. Make sure that alt account has already joined https://t.me/earlymemeacces

## Step 3 — Deploy to Render
1. Push this project to a GitHub repo (or connect Replit → GitHub)
2. On Render: New → Web Service → connect the repo
3. Build command: `pip install -r requirements.txt`
4. Start command: `python main.py`
5. Add these environment variables under Render's "Environment" tab:

| Key | Value |
|---|---|
| BOT_TOKEN | token from @BotFather |
| CHANNEL_ID | -1003710765715 |
| TELEGRAM_API_ID | 39801320 |
| TELEGRAM_API_HASH | 9efb94b33a2442c3d50302f4b1bc9313 |
| SESSION_STRING | the string from Step 2 |
| RAIDER_GROUP | earlymemeacces |

6. Deploy. Render will run the Flask keep-alive server + scheduler together.

## Step 4 — Keep it awake (if on Render's free tier)
Free web services on Render spin down after inactivity. Point UptimeRobot at your Render URL (pinging every 5 min) to keep it alive, same as your other bots.

## Notes
- Coin dedupe and raider-message tracking are kept in memory — they reset if the bot restarts, so you might see a small repeat batch right after a redeploy. Not a big deal at this scale.
- To add/remove chains, edit the `NETWORKS` list in `main.py`.
- To tune which messages count as "raider jobs," edit `RAIDER_KEYWORDS` in `main.py`.
