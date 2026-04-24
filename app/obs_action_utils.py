import shutil
import re
import time
from pathlib import Path
import obsws_python as obs

from .enums import ClipType
from .state import get_state_for_api, get_current_match_id
from .actual_match import ActualMatch


HOST = "127.0.0.1"
PORT = 4455
PASSWORD = "obswsVCSE2026"
MEDIA_SOURCE_INPUT_NAME = "replay_media_source"
VLC_SOURCE_INPUT_NAME = "szcse_vlc_source"
LIVE_SCENE = "szcse_livescore"
VLC_SCENE = "szcse_vlc"
SZCSE_ADMIN_USER = "vcse"
SZCSE_ADMIN_PW = "VIHAR2026sarok"

actual_match = ActualMatch(match_id=get_current_match_id())

def is_new_match(new_match_id) -> bool:
    global actual_match

    #print(f"Match ID UPDATE | actual: {actual_match.match_id} -> new:{new_match_id}")
    if actual_match.match_id == new_match_id:
        #print(f"same match id: {actual_match.match_id}")
        return False
    elif new_match_id == "no_match":
        return False
    else:
        #print(f"new match id: {new_match_id}")
        actual_match = ActualMatch(match_id=new_match_id)
        return True


def save_goal(replay_name):
    state = get_state_for_api()

    actual_set = state["score"]["sets_left"] + state["score"]["sets_right"] + 1

    actual_match.last_goal = replay_name
    # if the actual set does not exist just declare with empty list
    if actual_set not in actual_match.match_clips.keys():
        actual_match.match_clips[actual_set] = []

    actual_match.match_clips[actual_set].append(replay_name)
    print(f'clips: {actual_match.match_clips}')

def save_fault(replay_name):
    actual_match.last_fault = replay_name

def save_other(replay_name):
    state = get_state_for_api()

    actual_set = state["score"]["sets_left"] + state["score"]["sets_right"] + 1
    # if the actual set does not exist just declare with empty list
    if actual_set not in actual_match.match_clips.keys():
        actual_match.match_clips[actual_set] = []

    actual_match.match_clips[actual_set].append(replay_name)
    print(f'clips: {actual_match.match_clips}')

def replay_last_set():
    print("replay_last_set...")

    state = get_state_for_api()

    actual_set = state["score"]["sets_left"] + state["score"]["sets_right"] + 1
    goals_left, goals_right = state["score"]["goals_left"], state["score"]["goals_right"]

    set_to_replay = 0

    if actual_set == 1:
        set_to_replay = 1
    else:
        if goals_left + goals_right == 0:
            set_to_replay = actual_set - 1
        else:
            set_to_replay = actual_set

    videos = actual_match.match_clips[set_to_replay]
    with obs.ReqClient(host=HOST, port=PORT, password=PASSWORD, timeout=5) as cl:
        # Build playlist
        playlist = []
        for i, video in enumerate(videos):
            path = Path(video).resolve().as_uri()  # -> file:///...
            playlist.append({
                "value": path,
                "selected": i == 0  # first video starts
            })

        settings = {
            "playlist": playlist
        }

        # Apply playlist to VLC source
        cl.set_input_settings(
            VLC_SOURCE_INPUT_NAME,
            settings,
            overlay=False  # replace existing playlist
        )

        # Switch to VLC scene
        cl.set_current_program_scene(VLC_SCENE)

        # Start playback explicitly
        cl.trigger_media_input_action(
            VLC_SOURCE_INPUT_NAME,
            "OBS_WEBSOCKET_MEDIA_INPUT_ACTION_RESTART"
        )


def replay_match():
    print("replay_match...")
    videos = [video for sublist in actual_match.match_clips.values() for video in sublist]
    with obs.ReqClient(host=HOST, port=PORT, password=PASSWORD, timeout=5) as cl:
        # Build playlist
        playlist = []
        for i, video in enumerate(videos):
            path = Path(video).resolve().as_uri()  # -> file:///...
            playlist.append({
                "value": path,
                "selected": i == 0  # first video starts
            })

        settings = {
            "playlist": playlist
        }

        # Apply playlist to VLC source
        cl.set_input_settings(
            VLC_SOURCE_INPUT_NAME,
            settings,
            overlay=False  # replace existing playlist
        )

        # Switch to VLC scene
        cl.set_current_program_scene(VLC_SCENE)

        # Start playback explicitly
        cl.trigger_media_input_action(
            VLC_SOURCE_INPUT_NAME,
            "OBS_WEBSOCKET_MEDIA_INPUT_ACTION_RESTART"
        )


def back_to_live_scene():
    """
    Stops every playing Media and VLC source and switch to the live scene
    :return:
    """
    with obs.ReqClient(host=HOST, port=PORT, password=PASSWORD, timeout=5) as cl:
        try:
            cl.trigger_media_input_action(
                MEDIA_SOURCE_INPUT_NAME,
                "OBS_WEBSOCKET_MEDIA_INPUT_ACTION_STOP"
            )
        except Exception:
            pass

            # Stop VLC source
        try:
            cl.trigger_media_input_action(
                VLC_SOURCE_INPUT_NAME,
                "OBS_WEBSOCKET_MEDIA_INPUT_ACTION_STOP"
            )
        except Exception:
            pass

        # Switch scene
        cl.set_current_program_scene(LIVE_SCENE)



def replay_last_goal():
    print("replay_last_goal...")
    last_goal = actual_match.last_goal

    with obs.ReqClient(host=HOST, port=PORT, password=PASSWORD, timeout=3) as cl:
        # Set Media Source file path to the new replay file
        cl.set_input_settings(
            MEDIA_SOURCE_INPUT_NAME,
            settings={
                "local_file": last_goal,
                "is_local_file": True,
            },
            overlay=True
        )

        # Restart replay
        cl.trigger_media_input_action(MEDIA_SOURCE_INPUT_NAME, "OBS_WEBSOCKET_MEDIA_INPUT_ACTION_RESTART")


def replay_last_fault():
    print("replay_last_fault...")
    last_fault = actual_match.last_fault

    with obs.ReqClient(host=HOST, port=PORT, password=PASSWORD, timeout=3) as cl:
        # Set Media Source file path to the new replay file
        cl.set_input_settings(
            MEDIA_SOURCE_INPUT_NAME,
            settings={
                "local_file": last_fault,
                "is_local_file": True,
            },
            overlay=True
        )

        # Restart replay
        cl.trigger_media_input_action(MEDIA_SOURCE_INPUT_NAME, "OBS_WEBSOCKET_MEDIA_INPUT_ACTION_RESTART")


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


def save_replay_buffer() -> str:
    """
    Saves the replay buffer in OBS.
    And returns with the new file.
    """
    with obs.ReqClient(host=HOST, port=PORT, password=PASSWORD, timeout=5) as cl:
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

        return new_path


def get_last_replay() -> str:
    """
    Returns the name of the last replay.
    :return: The absolute path of the last replay.
    """
    time.sleep(0.5)
    with obs.ReqClient(host=HOST, port=PORT, password=PASSWORD, timeout=5) as cl:
        last_path = cl.get_last_replay_buffer_replay().saved_replay_path

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

    return f"{last_replay}_mid_{get_current_match_id()}_{players_and_match_state}_{clip_type.value}"


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




def obs_save_and_replay():
    print("obs_instant_replay called")

    new_replay_file = save_replay_buffer()

    with obs.ReqClient(host=HOST, port=PORT, password=PASSWORD, timeout=3) as cl:


        # Set Media Source file path to the new replay file
        cl.set_input_settings(
            MEDIA_SOURCE_INPUT_NAME,
            settings={
                "local_file": new_replay_file,
                "is_local_file": True,
            },
            overlay=True
        )


        # Restart replay
        cl.trigger_media_input_action(MEDIA_SOURCE_INPUT_NAME, "OBS_WEBSOCKET_MEDIA_INPUT_ACTION_RESTART")

        print("Media Source updated and restarted.")


def obs_replay_last_goal():
    print("obs_replay_last_goal called")


