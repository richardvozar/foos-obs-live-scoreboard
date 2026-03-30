import copy
import time
import threading
from .rules import required_sets_to_win, set_target

TEAM_SOURCE_URL_DEFAULT = "https://live.szegedicsocso.hu/table.php?tourid=101&tableid=1"

def now_ms():
    return int(time.time() * 1000)

def get_timeout_emoji(timeouts: int) -> str:
    if not isinstance(timeouts, int):
        timeouts = int(timeouts)
    timeout_emoji = '⏱️'
    used_timeout_emoji = '❌'

    #return timeout_emoji * timeouts + (2 - timeouts) * used_timeout_emoji
    return (2 - timeouts) * used_timeout_emoji

def new_state():
    return {
        "ts": now_ms(),
        "match": {
            "bo": "BO3",
            "teams": {"left": "Bal", "right": "Jobb"},
            "from_consolation_left": False,
            "from_consolation_right": False,
            "team_source_url": TEAM_SOURCE_URL_DEFAULT,
            "team_source_enabled": True,
            "team_source_last_ok_ts": None,
            "team_source_last_error": "",
        },
        "score": {
            "goals_left": 0,
            "goals_right": 0,
            "sets_left": 0,
            "sets_right": 0,
            "timeouts_left": 2,
            "timeouts_right": 2,
            "timeouts_left_string": get_timeout_emoji(2),
            "timeouts_right_string": get_timeout_emoji(2),
        },
        "meta": {"message": ""},
    }

_LOCK = threading.Lock()
_STATE = new_state()
_UNDO = []

def with_lock(fn):
    def wrapper(*args, **kwargs):
        with _LOCK:
            return fn(*args, **kwargs)
    return wrapper

@with_lock
def get_state_for_api():
    out = copy.deepcopy(_STATE)
    req_left, req_right = required_sets_to_win(_STATE)
    out["match"]["required_sets_left"] = req_left
    out["match"]["required_sets_right"] = req_right
    return out

@with_lock
def get_state_ref():
    # belső használatra (lock alatt hívod)
    return _STATE

@with_lock
def bump_ts():
    _STATE["ts"] = now_ms()

@with_lock
def push_undo():
    _UNDO.append(copy.deepcopy(_STATE))
    if len(_UNDO) > 200:
        _UNDO.pop(0)

@with_lock
def undo():
    global _STATE
    if _UNDO:
        _STATE = _UNDO.pop()
        _STATE["ts"] = now_ms()
        return True
    return False

def _match_over_unlocked():
    req_left, req_right = required_sets_to_win(_STATE)
    return _STATE["score"]["sets_left"] >= req_left or _STATE["score"]["sets_right"] >= req_right

def _reset_set_unlocked():
    _STATE["score"]["goals_left"] = 0
    _STATE["score"]["goals_right"] = 0
    _STATE["score"]["timeouts_left"] = 2
    _STATE["score"]["timeouts_right"] = 2
    _STATE["score"]["timeouts_left_string"] = get_timeout_emoji(2)
    _STATE["score"]["timeouts_right_string"] = get_timeout_emoji(2)

def _apply_set_win_unlocked(winner: str):
    if winner == "left":
        _STATE["score"]["sets_left"] += 1
        _STATE["meta"]["message"] = "Szett – Bal"
    else:
        _STATE["score"]["sets_right"] += 1
        _STATE["meta"]["message"] = "Szett – Jobb"
    _reset_set_unlocked()

def _check_auto_set_win_unlocked():
    left = _STATE["score"]["goals_left"]
    right = _STATE["score"]["goals_right"]
    target, win_by_2, cap = set_target(_STATE)

    if not win_by_2:
        if left >= target and left > right:
            _apply_set_win_unlocked("left")
        elif right >= target and right > left:
            _apply_set_win_unlocked("right")
        return

    if cap is not None and (left >= cap or right >= cap):
        if left == cap and left > right:
            _apply_set_win_unlocked("left")
        elif right == cap and right > left:
            _apply_set_win_unlocked("right")
        return

    if left >= target and (left - right) >= 2:
        _apply_set_win_unlocked("left")
    elif right >= target and (right - left) >= 2:
        _apply_set_win_unlocked("right")

@with_lock
def action_set_settings(payload: dict):
    bo = (payload.get("bo") or "BO3").upper()
    if bo not in ("BO1", "BO3", "BO5"):
        bo = "BO3"
    _STATE["match"]["bo"] = bo

    url = payload.get("team_source_url")
    if isinstance(url, str):
        _STATE["match"]["team_source_url"] = url.strip()

    en = payload.get("team_source_enabled")
    if isinstance(en, bool):
        _STATE["match"]["team_source_enabled"] = en

    left = payload.get("left")
    right = payload.get("right")
    if isinstance(left, str) and left.strip():
        _STATE["match"]["teams"]["left"] = left.strip()
    if isinstance(right, str) and right.strip():
        _STATE["match"]["teams"]["right"] = right.strip()

    consL = bool(payload.get("consLeft"))
    consR = bool(payload.get("consRight"))
    if bo == "BO1":
        consL = False
        consR = False
    if consL and consR:
        consR = False
    _STATE["match"]["from_consolation_left"] = consL
    _STATE["match"]["from_consolation_right"] = consR

    _STATE["meta"]["message"] = "Beállítások mentve"
    _STATE["ts"] = now_ms()

@with_lock
def action_set_consolation(side: str, value: bool):
    bo = (_STATE["match"]["bo"] or "BO3").upper()
    if bo == "BO1":
        _STATE["match"]["from_consolation_left"] = False
        _STATE["match"]["from_consolation_right"] = False
        _STATE["meta"]["message"] = "BO1-ben nincs vigaszág beállítás"
        _STATE["ts"] = now_ms()
        return

    if side == "left":
        _STATE["match"]["from_consolation_left"] = bool(value)
        if value:
            _STATE["match"]["from_consolation_right"] = False
    elif side == "right":
        _STATE["match"]["from_consolation_right"] = bool(value)
        if value:
            _STATE["match"]["from_consolation_left"] = False

    _STATE["meta"]["message"] = "Vigaszág beállítva"
    _STATE["ts"] = now_ms()

@with_lock
def action_swap_sides():
    m = _STATE["match"]
    s = _STATE["score"]

    m["teams"]["left"], m["teams"]["right"] = m["teams"]["right"], m["teams"]["left"]
    m["from_consolation_left"], m["from_consolation_right"] = m["from_consolation_right"], m["from_consolation_left"]

    s["goals_left"], s["goals_right"] = s["goals_right"], s["goals_left"]
    s["sets_left"], s["sets_right"] = s["sets_right"], s["sets_left"]
    s["timeouts_left"], s["timeouts_right"] = s["timeouts_right"], s["timeouts_left"]
    s["timeouts_left_string"], s["timeouts_right_string"] = s["timeouts_right_string"], s["timeouts_left_string"]

    _STATE["meta"]["message"] = "Oldalcsere"
    _STATE["ts"] = now_ms()

@with_lock
def action_reset_set():
    _reset_set_unlocked()
    _STATE["meta"]["message"] = "Szett reset"
    _STATE["ts"] = now_ms()

@with_lock
def action_reset_match():
    global _STATE
    bo = _STATE["match"]["bo"]
    teams = copy.deepcopy(_STATE["match"]["teams"])
    consL = _STATE["match"]["from_consolation_left"]
    consR = _STATE["match"]["from_consolation_right"]
    url = _STATE["match"]["team_source_url"]
    en = _STATE["match"]["team_source_enabled"]

    _STATE = new_state()
    _STATE["match"]["bo"] = bo
    _STATE["match"]["teams"] = teams
    _STATE["match"]["from_consolation_left"] = consL
    _STATE["match"]["from_consolation_right"] = consR
    _STATE["match"]["team_source_url"] = url
    _STATE["match"]["team_source_enabled"] = en
    _STATE["meta"]["message"] = "Match reset"
    _STATE["ts"] = now_ms()

@with_lock
def action_goal(side: str, delta: int):
    if _match_over_unlocked():
        _STATE["meta"]["message"] = "Match vége – resetelj a folytatáshoz"
        _STATE["ts"] = now_ms()
        return

    if side == "left":
        _STATE["score"]["goals_left"] = max(0, _STATE["score"]["goals_left"] + delta)
        _STATE["meta"]["message"] = "Gól – Bal" if delta > 0 else "Bal gól -1"
    else:
        _STATE["score"]["goals_right"] = max(0, _STATE["score"]["goals_right"] + delta)
        _STATE["meta"]["message"] = "Gól – Jobb" if delta > 0 else "Jobb gól -1"

    if delta > 0:
        _check_auto_set_win_unlocked()

    _STATE["ts"] = now_ms()

@with_lock
def action_timeout(side: str):
    if side == "left":
        if _STATE["score"]["timeouts_left"] > 0:
            _STATE["score"]["timeouts_left"] -= 1
            _STATE["score"]["timeouts_left_string"] = get_timeout_emoji(_STATE["score"]["timeouts_left"])
            _STATE["meta"]["message"] = "Időkérés – Bal"
        else:
            _STATE["meta"]["message"] = "Bal: nincs több időkérés ebben a szettben"
    else:
        if _STATE["score"]["timeouts_right"] > 0:
            _STATE["score"]["timeouts_right"] -= 1
            _STATE["score"]["timeouts_right_string"] = get_timeout_emoji(_STATE["score"]["timeouts_right"])
            _STATE["meta"]["message"] = "Időkérés – Jobb"
        else:
            _STATE["meta"]["message"] = "Jobb: nincs több időkérés ebben a szettben"
    _STATE["ts"] = now_ms()

@with_lock
def update_team_names(left_name: str | None, right_name: str | None):
    changed = False
    if left_name and left_name != _STATE["match"]["teams"]["left"]:
        _STATE["match"]["teams"]["left"] = left_name
        changed = True
    if right_name and right_name != _STATE["match"]["teams"]["right"]:
        _STATE["match"]["teams"]["right"] = right_name
        changed = True

    if changed:
        _STATE["meta"]["message"] = "Csapatnevek frissítve (API)"
    _STATE["match"]["team_source_last_ok_ts"] = now_ms()
    _STATE["match"]["team_source_last_error"] = ""
    _STATE["ts"] = now_ms()

@with_lock
def set_team_source_error(err: str):
    _STATE["match"]["team_source_last_error"] = err[:500]
    _STATE["ts"] = now_ms()