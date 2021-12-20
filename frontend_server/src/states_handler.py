from typing import List, Optional

import user_message_pb2 as um

from states import State


class StatesHandlers:
    def __init__(self, handlers):
        self.__handlers = handlers

    def try_handle(self, request: um.UserMessage, state: Optional[State]) -> Optional[List[um.ServerResponse]]:
        if state is None:
            return None
        if state.action in self.__handlers:
            return self.__handlers[state.action].handle_request(request)
        return None
