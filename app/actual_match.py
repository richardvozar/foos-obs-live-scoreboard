class ActualMatch:
    def __init__(self, match_id):
        self._match_id: str = match_id
        self.actual_set: int = 0
        self._last_goal: str = ''
        self._last_fault: str = ''
        self._match_clips: dict[int, list[str]] = {1: []}


    @property
    def match_id(self) -> str:
        return self._match_id

    @match_id.setter
    def match_id(self, match_id: str):
        self._match_id = match_id

    @property
    def last_goal(self) -> str:
        if self._last_goal:
            return self._last_goal
        else:
            return "HIBA! Nem volt még gól mentve ezen a meccsen!"

    @last_goal.setter
    def last_goal(self, last_goal: str):
        self._last_goal = last_goal

    @property
    def last_fault(self) -> str:
        return self._last_fault

    @last_fault.setter
    def last_fault(self, last_fault: str):
        self._last_fault = last_fault

    @property
    def match_clips(self) -> dict[int, list[str]]:
        return self._match_clips

    def __eq__(self, __value):
        return self._match_id == __value.match_id

    def reset_set(self):
        self._last_goal = ''
        self._last_fault = ''

    def get_set_clips(self, _set: int) -> list:
        return self._match_clips[_set]




