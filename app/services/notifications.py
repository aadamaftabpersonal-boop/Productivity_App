"""Notification services including Discord webhook pings for resurfacing pings."""
import httpx
from typing import List, Dict, Any


async def send_discord_resurface_ping(webhook_url: str, user_name: str, active_weaknesses: List[Dict[str, Any]]) -> bool:
    """Sends an embed ping to user's Discord webhook channel when resurfacing items are due."""
    if not webhook_url or not webhook_url.startswith("https://discord.com/api/webhooks/"):
        return False

    weakness_names = [w.get("concept", "Algorithm Pattern") for w in active_weaknesses[:3]]
    embed = {
        "title": "⚡ CP Hub — Spaced Repetition Resurface Ping",
        "description": f"Hey **{user_name}**, {len(active_weaknesses)} weakness gap(s) are ready for virtual contest resurfacing!",
        "color": 15844367,  # Amber gold
        "fields": [
            {
                "name": "Target Weaknesses",
                "value": "\n".join([f"• `{name}`" for name in weakness_names]) or "• General CP Practice",
                "inline": False,
            },
            {
                "name": "Action Recommended",
                "value": "Open [CP Hub Dashboard](http://localhost:5173/) to complete your 30-minute practice rep.",
                "inline": False,
            }
        ],
        "footer": {"text": "CP Hub → Empirical OA Prep Engine"}
    }

    payload = {"username": "CP Hub Bot", "embeds": [embed]}

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.post(webhook_url, json=payload)
            return resp.status_code in (200, 204)
    except Exception:
        return False
