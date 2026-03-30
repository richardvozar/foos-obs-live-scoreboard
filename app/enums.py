from enum import Enum

class ClipType(Enum):
    LEFT_GOAL = "left_goal"
    RIGHT_GOAL = "right_goal"

    LEFT_5TO3_PASS = "left_5to3_pass"
    RIGHT_5TO3_PASS = "right_5to3_pass"

    LEFT_2TO3_PASS = "left_2to3_pass"
    RIGHT_2TO3_PASS = "right_2to3_pass"

    LEFT_SHOT_NOGOAL = "left_shot_nogoal"
    RIGHT_SHOT_NOGOAL = "right_shot_nogoal"

    FAULT = "fault"