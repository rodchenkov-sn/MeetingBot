from abc import ABC, abstractmethod
from typing import List

import user_message_pb2 as um

class RequestHandler(ABC):
    @abstractmethod
    def handle_request(self, request) -> List[um.ServerResponse]:
        pass
