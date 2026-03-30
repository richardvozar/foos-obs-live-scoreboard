import shutil
import re
import time
from pathlib import Path
import obsws_python as obs

from .enums import ClipType
from .state import get_state_for_api


HOST = "127.0.0.1"
PORT = 4455
PASSWORD = "obswsVCSE2026"
MEDIA_SOURCE_INPUT_NAME = "replay_media_source"


def sanitize_names(name: str) -> str:
    """
    Filename without áéíóöőúüű, without spaces and special characters.
    """
    name = re.sub(r'[<>:"/\\|?*]', "_", name)
    name = re.sub(r'[óöő]', "o", name)
    name = re.sub(r'[ÓÖŐ]', "O", name)
    name = re.sub(r'[úüű]', "u", name)
    name = re.sub(r'[ÚÜŰ]', "U", name)
    name = name.replace(" ", "")
    name = name.replace("á", "a")
    name = name.replace("Á", "A")
    name = name.replace("é", "e")
    name = name.replace("É", "E")
    name = name.replace("í", "i")
    name = name.replace("Í", "I")
    name = name.replace("-", "_")
    name = name.strip().rstrip(".")
    return name if name else "error_in_names"


def save_replay_buffer():
    """
    Saves the replay buffer in OBS.
    """
    with obs.ReqClient(host=HOST, port=PORT, password=PASSWORD, timeout=5) as cl:
        # Check if the Replay Buffer is running
        status = cl.get_replay_buffer_status()
        if not status.output_active:
            cl.start_replay_buffer()
            # give it a little time to actually start
            time.sleep(0.25)

        cl.save_replay_buffer()


def get_last_replay() -> str:
    """
    Returns the name of the last replay.
    :return: The absolute path of the last replay.
    """
    with obs.ReqClient(host=HOST, port=PORT, password=PASSWORD, timeout=5) as cl:
        last_path = cl.get_last_replay_buffer_replay().saved_replay_path
        print(last_path)
    if not last_path:
        print("Nem található legutóbb mentett replay fájl.")
    return last_path


def get_players_and_match_state() -> str:
    state = get_state_for_api()

    team_left = state["match"]["teams"]["left"]
    team_right = state["match"]["teams"]["right"]

    team_left = sanitize_names(team_left)
    team_right = sanitize_names(team_right)

    goals_left = state["score"]["goals_left"]
    goals_right = state["score"]["goals_right"]

    sets_left = state["score"]["sets_left"]
    sets_right = state["score"]["sets_right"]

    return f"{team_left}_VS_{team_right}_sets_{sets_left}_VS_{sets_right}_goals_{goals_left}_VS_{goals_right}"


def construct_replay_name(clip_type: ClipType) -> str:
    """
    Gets the name of the last replay. Because it is a timestamp it uses it, but extends the name
    with players names and with goal type (e.g.: left_goal, right_2to3_pass).
    :param clip_type: type of the clip like fault or right_shot_nogoal etc.
    :return: new name of the clip with details
    """
    last_replay = get_last_replay().split("/")[-1]
    last_replay = last_replay.replace("Replay ", "").replace(" ", "-").replace(".mp4", "")
    players_and_match_state = get_players_and_match_state()

    return f"{last_replay}_{players_and_match_state}_{clip_type.value}"


def rename_last_replay(original_path: str, new_name: str) -> str:
    """
    Renames a file in the same folder.

    :param original_path: original file's absolute path
    :param new_name: new filename without extension
    :return: The new file's absolute path
    """

    src = Path(original_path)
    if not src.exists():
        print(f"Nem létezik a fájl: {src}")
    dst = src.with_name(f"{new_name}{src.suffix}")
    shutil.copy(src, dst)
    return str(dst)


def obs_instant_replay():
    print("obs_instant_replay called")

    with obs.ReqClient(host=HOST, port=PORT, password=PASSWORD, timeout=3) as cl:
        # 1)
        rb = cl.get_replay_buffer_status()
        if not rb.output_active:
            cl.start_replay_buffer()
            # give it a little time to actually start
            time.sleep(0.25)

        # 2) Last saved replay path (for polling)
        prev = cl.get_last_replay_buffer_replay().saved_replay_path

        # 3) Save Replay Buffer
        cl.save_replay_buffer()

        # 4) Wait for OBS to save the last replay path
        new_path = None
        deadline = time.time() + 5.0  # max 5 sec wait
        while time.time() < deadline:
            cur = cl.get_last_replay_buffer_replay().saved_replay_path
            if cur and cur != prev:
                new_path = cur
                break
            time.sleep(0.1)

        if not new_path:
            print(
                "Nem kaptam új saved_replay_path-ot. "
                "Ellenőrizd: Replay Buffer be van-e kapcsolva OBS-ben, és van-e jogosultság/írási útvonal."
            )

        print(f"Új replay fájl: {new_path}")

        # 5) Set Media Source file path to the new replay file
        cl.set_input_settings(
            MEDIA_SOURCE_INPUT_NAME,
            settings={
                "local_file": new_path,
                "is_local_file": True,
            },
            overlay=True
        )

        # 6) Restart replay
        cl.trigger_media_input_action(MEDIA_SOURCE_INPUT_NAME, "OBS_WEBSOCKET_MEDIA_INPUT_ACTION_RESTART")

        print("Media Source updated and restarted.")