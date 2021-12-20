from typing import Optional

class State:
    def __init__(self, _action: str, _argument: int, _arg2: int = 1):
        self.action = _action
        self.argument = _argument
        self.argument2 = _arg2


class StateRepo:
    def __init__(self):
        self.__states = {}
    
    def set_state(self, user: int, state: State):
        self.__states[user] = state

    def get_state(self, user: int) -> Optional[State]:
        if user in self.__states:
            return self.__states[user]
        return None

    def clear_state(self, user: int):
        self.__states.pop(user)
