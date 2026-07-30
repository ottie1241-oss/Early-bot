import os
import time
import logging
import requests
from datetime import datetime, timezone
from threading import Thread
from flask import Flask
from apscheduler.schedulers.background import BackgroundScheduler
from telethon.sync import TelegramClient
from telethon.sessions import StringSession

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger("memebot")

# ---------- ENV VARS (set these on Render) ----------
BOT_TOKEN = os.environ["BOT_TOKEN"]                # from @BotFather
CHANNEL_ID = os.environ["CHANNEL_ID"]               # e.g. -1003710765715
TELEGRAM_API_ID = int(os.environ["TELEGRAM_API_ID"])       # alt account's api_id
TELEGRAM_API_HASH = os.environ["TELEGRAM_API_HASH"]        # alt account's api_hash
SESSION_STRING = os.environ["SESSION_STRING"]       # from generate_session.py
RAIDER_GROUP = os.environ.get("RAIDER_GROUP", "earlymemeacces")

TELEGRAM_SEND_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

# Chains to scan on GeckoTerminal (network ids per their API)
NETWORKS = ["eth", "bsc", "solana", "base", "arbitrum", "polygon_pos"]

# How far back counts as "new" for a scan cycle (minutes)
LOOKBACK_MINUTES = 35

# Keywords that flag a message as a raider-job / raid-hiring post
RAIDER_KEYWORDS = [
    "raider", "raiders needed", "hiring raiders", "join our raid",
    "raid team", "looking for raiders", "raid job", "recruiting raiders",
    "raid campaign", "earn per raid", "raiding job", "become a raider",
]

# in-memory dedupe stores (reset on process restart, that's fine)
seen_pools = set()
last_raider_msg_id = {"id": 0}


def send_to_channel(text):
    try:
        resp = requests.post(
            TELEGRAM_SEND_URL,
            data={
                "chat_id": CHANNEL_ID,
                "text": text,
                "parse_mode": "HTML",
                "disable_web_page_preview": False,
            },
            timeout=15,
        )
        if not resp.ok:
            log.error(f"Failed to send message: {resp.text}")
    except Exception as e:
        log.error(f"Error sending message: {e}")


def fetch_new_pools(network):
    url = f"https://api.geckoterminal.com/api/v2/networks/{network}/new_pools"
    try:
        resp = requests.get(url, timeout=15, headers={"Accept": "application/json"})
        if not resp.ok:
            log.warning(f"GeckoTerminal {network} returned {resp.status_code}")
            return []
        return resp.json().get("data", [])
    except Exception as e:
        log.error(f"Error fetching pools for {network}: {e}")
        return []


def job_new_coins():
    log.info("Running new-coins job...")
    now = datetime.now(timezone.utc)
    candidates = []

    for network in NETWORKS:
        for pool in fetch_new_pools(network):
            attrs = pool.get("attributes", {})
            pool_id = pool.get("id")
            created_at_str = attrs.get("pool_created_at")
            if not created_at_str or pool_id in seen_pools:
                continue

            try:
                created_at = datetime.fromisoformat(created_at_str.replace("Z", "+00:00"))
            except ValueError:
                continue

            age_minutes = (now - created_at).total_seconds() / 60
            if age_minutes > LOOKBACK_MINUTES:
                continue

            candidates.append({
                "id": pool_id,
                "network": network,
                "name": attrs.get("name", "Unknown"),
                "price_usd": attrs.get("base_token_price_usd"),
                "liquidity_usd": attrs.get("reserve_in_usd"),
                "created_at": created_at,
                "url": f"https://www.geckoterminal.com/{network}/pools/{pool_id.split('_')[-1]}",
            })

    candidates.sort(key=lambda c: c["created_at"], reverse=True)
    top = candidates[:10]

    if not top:
        log.info("No new coins found this cycle.")
        return

    for coin in top:
        seen_pools.add(coin["id"])
        liq = coin["liquidity_usd"]
        liq_str = f"${float(liq):,.0f}" if liq else "N/A"
        price = coin["price_usd"]
        price_str = f"${float(price):.8f}" if price else "N/A"

        msg = (
            f"🆕 <b>{coin['name']}</b>\n"
            f"⛓ Chain: {coin['network']}\n"
            f"💧 Liquidity: {liq_str}\n"
            f"💵 Price: {price_str}\n"
            f"🔗 {coin['url']}"
        )
        send_to_channel(msg)
        time.sleep(1)  # avoid hitting Telegram rate limits

    log.info(f"Posted {len(top)} new coins.")


def job_raider_scan():
    log.info("Running raider-job scan...")
    try:
        with TelegramClient(StringSession(SESSION_STRING), TELEGRAM_API_ID, TELEGRAM_API_HASH) as client:
            messages = client.get_messages(RAIDER_GROUP, limit=50, min_id=last_raider_msg_id["id"])
            if not messages:
                log.info("No new messages in raider group.")
                return

            hits = []
            highest_id = last_raider_msg_id["id"]
            for m in messages:
                highest_id = max(highest_id, m.id)
                if not m.text:
                    continue
                lowered = m.text.lower()
                if any(kw in lowered for kw in RAIDER_KEYWORDS):
                    hits.append(m.text)

            last_raider_msg_id["id"] = highest_id

            for text in hits:
                snippet = text if len(text) < 500 else text[:500] + "..."
                send_to_channel(f"🎯 <b>Possible raider job</b>\n\n{snippet}")
                time.sleep(1)

            log.info(f"Found {len(hits)} raider-job matches.")
    except Exception as e:
        log.error(f"Error scanning raider group: {e}")


# ---------- Keep-alive web server (for Render + UptimeRobot) ----------
app = Flask(__name__)


@app.route("/")
def home():
    return "Bot is alive."


def run_web():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)


if __name__ == "__main__":
    Thread(target=run_web).start()

    scheduler = BackgroundScheduler()
    scheduler.add_job(job_new_coins, "interval", minutes=30, next_run_time=datetime.now())
    scheduler.add_job(job_raider_scan, "interval", minutes=30, next_run_time=datetime.now())
    scheduler.start()

    log.info("Scheduler started. Bot is running.")
    while True:
        time.sleep(60)
