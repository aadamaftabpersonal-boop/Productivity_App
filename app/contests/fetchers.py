import httpx
from datetime import datetime, timezone

CODEFORCES_API = "https://codeforces.com/api/contest.list"
LEETCODE_GRAPHQL = "https://leetcode.com/graphql"

LEETCODE_QUERY = """
query upcomingContests {
  upcomingContests {
    title
    titleSlug
    startTime
    duration
  }
}
"""


async def fetch_codeforces_contests() -> list[dict]:
    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.get(CODEFORCES_API)
        resp.raise_for_status()
        data = resp.json()

    if data.get("status") != "OK":
        raise ValueError("Codeforces API returned non-OK status")

    contests = []
    for c in data["result"]:
        # only keep upcoming/current; skip old finished ones to avoid importing years of history
        if c["phase"] not in ("BEFORE", "CODING"):
            continue
        contests.append({
            "platform": "codeforces",
            "external_id": str(c["id"]),
            "name": c["name"],
            "start_time": datetime.fromtimestamp(c["startTimeSeconds"], tz=timezone.utc) if c.get("startTimeSeconds") else None,
            "duration_seconds": c["durationSeconds"],
            "url": f"https://codeforces.com/contest/{c['id']}",
            "is_finished": c["phase"] == "FINISHED",
        })
    return [c for c in contests if c["start_time"] is not None]


async def fetch_leetcode_contests() -> list[dict]:
    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.post(LEETCODE_GRAPHQL, json={"query": LEETCODE_QUERY})
        resp.raise_for_status()
        data = resp.json()

    upcoming = data.get("data", {}).get("upcomingContests", [])
    contests = []
    for c in upcoming:
        contests.append({
            "platform": "leetcode",
            "external_id": c["titleSlug"],
            "name": c["title"],
            "start_time": datetime.fromtimestamp(c["startTime"], tz=timezone.utc),
            "duration_seconds": c["duration"],
            "url": f"https://leetcode.com/contest/{c['titleSlug']}",
            "is_finished": False,
        })
    return contests