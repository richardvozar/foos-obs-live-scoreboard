from .obs_action_utils import *

def button_function_1():
    print("INSTANT REPLAY: GÓL")
    obs_instant_replay()


def button_function_2():
    print("KLIPP MENTÉS: Bal csapat középpálya passz")
    replay_name = construct_replay_name(ClipType.LEFT_5TO3_PASS)
    rename_last_replay(get_last_replay(), replay_name)


def button_save_goal():
    print("Button: button_save_goal")
def button_save_fault():
    print("Button: button_save_fault")
def button_save_other():
    print("Button: button_save_other")
def button_replay_goal():
    print("Button: button_replay_goal")
def button_replay_fault():
    print("Button: button_replay_fault")
def button_replay_set():
    print("Button: button_replay_set")
def button_replay_match():
    print("Button: button_replay_match")
def button_back_to_live():
    print("Button: button_back_to_live")
