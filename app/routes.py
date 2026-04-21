from flask import Blueprint, jsonify, render_template, request
from . import state as S
from .obs_actions import (
    button_save_goal, button_save_fault, button_save_other, button_replay_goal,
    button_replay_fault, button_replay_set, button_replay_match, button_back_to_live
)

bp = Blueprint("main", __name__)

@bp.get("/")
def index():
    return render_template("index.html")

@bp.get("/control")
def control():
    return render_template("control.html")

@bp.get("/overlay")
def overlay():
    return render_template("overlay.html")

@bp.get("/state")
def state():
    return jsonify(S.get_state_for_api())

@bp.post("/action")
def action():
    payload = request.get_json(force=True, silent=True) or {}
    action = (payload.get("action") or "").strip()

    if not action:
        return jsonify({"ok": False, "error": "Missing action"}), 400

    if action == "undo":
        ok = S.undo()
        return jsonify({"ok": True, "undone": ok})

    # minden módosító művelet előtt undo snapshot
    S.push_undo()

    if action == "set_settings":
        S.action_set_settings(payload)
        return jsonify({"ok": True})

    if action == "set_consolation":
        side = payload.get("side")
        value = bool(payload.get("value"))
        if side not in ("left", "right"):
            return jsonify({"ok": False, "error": "Invalid side"}), 400
        S.action_set_consolation(side, value)
        return jsonify({"ok": True})

    if action == "swap_sides":
        S.action_swap_sides()
        return jsonify({"ok": True})

    if action == "reset_set":
        S.action_reset_set()
        return jsonify({"ok": True})

    if action == "reset_match":
        S.action_reset_match()
        return jsonify({"ok": True})

    if action == "goal_left":
        S.action_goal("left", +1)
        return jsonify({"ok": True})

    if action == "goal_right":
        S.action_goal("right", +1)
        return jsonify({"ok": True})

    if action == "goal_left_minus":
        S.action_goal("left", -1)
        return jsonify({"ok": True})

    if action == "goal_right_minus":
        S.action_goal("right", -1)
        return jsonify({"ok": True})

    if action == "timeout_left":
        S.action_timeout("left")
        return jsonify({"ok": True})

    if action == "timeout_right":
        S.action_timeout("right")
        return jsonify({"ok": True})


    if action == "button_save_goal":
        button_save_goal()
        return jsonify({"ok": True})

    if action == "button_save_fault":
        button_save_fault()
        return jsonify({"ok": True})

    if action == "button_save_other":
        button_save_other()
        return jsonify({"ok": True})

    if action == "button_replay_goal":
        button_replay_goal()
        return jsonify({"ok": True})

    if action == "button_replay_fault":
        button_replay_fault()
        return jsonify({"ok": True})

    if action == "button_replay_set":
        button_replay_set()
        return jsonify({"ok": True})

    if action == "button_replay_match":
        button_replay_match()
        return jsonify({"ok": True})

    if action == "button_back_to_live":
        button_back_to_live()
        return jsonify({"ok": True})



    # ismeretlen action: undo push visszavonása (egyszerűen pop)
    # (nem kritikus, de tiszta)
    # NOTE: mivel a push_undo lock alatt fut, itt is lock kéne a közvetlen pophoz.
    # egyszerűen hagyjuk: ismeretlen action ritka; max egy felesleges undo entry.
    return jsonify({"ok": False, "error": f"Unknown action: {action}"}), 400