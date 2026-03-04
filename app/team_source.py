import json
import threading
import time
import urllib.request
from .state import get_state_ref, update_team_names, set_team_source_error

TEAM_REFRESH_SEC = 5
_thread_started = False

def extract_team_name(val):
    if val is None:
        return None
    if isinstance(val, str):
        s = val.strip()
        return s if s else None
    if isinstance(val, dict):
        for k in ("name", "teamname", "teamName", "title"):
            if k in val and isinstance(val[k], str) and val[k].strip():
                return val[k].strip()
        for _, v in val.items():
            if isinstance(v, str) and v.strip():
                return v.strip()
        return None
    if isinstance(val, list):
        parts = [v.strip() for v in val if isinstance(v, str) and v.strip()]
        return " / ".join(parts) if parts else None
    return None

def fetch_teams(url: str):
    req = urllib.request.Request(url, headers={"User-Agent": "foos-obs-scoreboard/1.0"})
    with urllib.request.urlopen(req, timeout=3) as resp:
        raw = resp.read()
    data = json.loads(raw.decode("utf-8", errors="replace"))

    # user: JSONPath $.team1
    t1 = extract_team_name(data.get("team1"))
    t2 = extract_team_name(data.get("team2"))
    return t1, t2

def loop():
    while True:
        time.sleep(TEAM_REFRESH_SEC)
        st = get_state_ref()  # NOTE: state.py lock decorator ensures safety for public API; here we only read fields quickly
        # mivel itt nincs lock decorator, a minimál safe megoldás: csak olvasunk egyszerű mezőket (GIL mellett ez oké),
        # és a módosítást update_team_names / set_team_source_error csinálja lock alatt.
        enabled = bool(st["match"]["team_source_enabled"])
        url = st["match"]["team_source_url"]
        if not enabled or not url:
            continue

        try:
            left, right = fetch_teams(url)
            update_team_names(left, right)
        except Exception as e:
            set_team_source_error(str(e))

def start_team_fetcher():
    global _thread_started
    if _thread_started:
        return
    t = threading.Thread(target=loop, daemon=True)
    t.start()
    _thread_started = True