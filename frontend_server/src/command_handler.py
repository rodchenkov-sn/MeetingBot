import re

from typing import List, Optional

import user_message_pb2 as um


class CommandHandlers:
    def __init__(self, handlers):
        self.__handlers = handlers

    def try_handle(self, requiest: um.UserMessage) -> Optional[List[um.ServerResponse]]:
        match = re.search(r'\/[a-z_]+', requiest.text)
        if match is None:
            return None
        cmd = match.group()
        if cmd in self.__handlers:
            return self.__handlers[cmd].handle_request(requiest)
        return None
