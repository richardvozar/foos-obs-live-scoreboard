def rules_for(bo: str):
    bo = (bo or "BO3").upper()
    if bo == "BO1":
        return {"mode": "BO1", "normal_set_goal": 7, "final_win_by_2": False, "final_cap": None}
    if bo == "BO3":
        return {"mode": "BO3", "normal_set_goal": 5, "final_win_by_2": True, "final_cap": 8}
    return {"mode": "BO5", "normal_set_goal": 5, "final_win_by_2": True, "final_cap": 8}

def required_sets_to_win(state):
    """
    BO1: 1
    BO3: 2
    BO5: 3
    If exactly one side is from_consolation -> that side needs +1 set.
    """
    bo = (state["match"]["bo"] or "BO3").upper()
    base = 1 if bo == "BO1" else (2 if bo == "BO3" else 3)

    lc = bool(state["match"]["from_consolation_left"])
    rc = bool(state["match"]["from_consolation_right"])

    req_left = base + (1 if lc and not rc else 0)
    req_right = base + (1 if rc and not lc else 0)
    return req_left, req_right

def is_final_set(state):
    r = rules_for(state["match"]["bo"])
    if r["mode"] == "BO1":
        return True
    req_left, req_right = required_sets_to_win(state)
    return (state["score"]["sets_left"] == req_left - 1) and (state["score"]["sets_right"] == req_right - 1)

def set_target(state):
    r = rules_for(state["match"]["bo"])
    if r["mode"] == "BO1":
        return r["normal_set_goal"], False, None
    if is_final_set(state):
        return r["normal_set_goal"], r["final_win_by_2"], r["final_cap"]
    return r["normal_set_goal"], False, None