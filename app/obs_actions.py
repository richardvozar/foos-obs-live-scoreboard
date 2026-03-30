from .obs_action_utils import *

def button_function_1():
    print("INSTANT REPLAY: GÓL")
    obs_instant_replay()


def button_function_2():
    print("KLIPP MENTÉS: Bal csapat középpálya passz")
    replay_name = construct_replay_name(ClipType.LEFT_5TO3_PASS)
    rename_last_replay(get_last_replay(), replay_name)

def button_function_3():
    print("KLIPP MENTÉS: Jobb csapat középpálya passz")

def button_function_4():
    print("KLIPP MENTÉS: Bal csapat kapus passz")

def button_function_5():
    print("KLIPP MENTÉS: Jobb csapat kapus passz")

def button_function_6():
    print("KLIPP MENTÉS: Bal csapat lövés - ellenfél védi")

def button_function_7():
    print("KLIPP MENTÉS: Jobb csapat lövés - ellenfél védi")

def button_function_8():
    print("INSTANT REPLAY: FAULT")

def button_function_9():
    print("VISSZAJÁTSZÁS: legutóbbi gól")

def button_function_10():
    print("VISSZAJÁTSZÁS: legutóbbi mentett klipp")

def button_function_11():
    print("VISSZAJÁTSZÁS: legutóbbi fault szituáció")

def button_function_12():
    print("VISSZAJÁTSZÁS: Eddigi szett (aktuális)")

def button_function_13():
    print("VISSZAJÁTSZÁS: Előző szett")

def button_function_14():
    print("VISSZAJÁTSZÁS: Teljes meccs")

def button_function_15():
    print("Replay megállítása, és azonnal visszatérés az ÉLŐ adásra")