from .obs_action_utils import *


def button_save_goal():
    print("Button: button_save_goal")
    obs_save_and_replay()
    replay_name = construct_replay_name(ClipType.GOAL)
    renamed_file = rename_last_replay(get_last_replay(), replay_name)
    save_goal(renamed_file)

def button_save_fault():
    print("Button: button_save_fault")
    save_replay_buffer()
    replay_name = construct_replay_name(ClipType.FAULT)
    renamed_file = rename_last_replay(get_last_replay(), replay_name)
    save_fault(renamed_file)

def button_save_other():
    print("Button: button_save_other")
    save_replay_buffer()
    replay_name = construct_replay_name(ClipType.OTHER)
    renamed_file = rename_last_replay(get_last_replay(), replay_name)
    save_other(renamed_file)

def button_replay_goal():
    print("Button: button_replay_goal")
    replay_last_goal()

def button_replay_fault():
    print("Button: button_replay_fault")
    replay_last_fault()

def button_replay_set():
    print("Button: button_replay_set")
    replay_last_set()

def button_replay_match():
    print("Button: button_replay_match")
    replay_match()

def button_back_to_live():
    print("Button: button_back_to_live")
    back_to_live_scene()

def update_match_id(match_id):
    is_new = is_new_match(match_id)
    if is_new:
        print("New match found")