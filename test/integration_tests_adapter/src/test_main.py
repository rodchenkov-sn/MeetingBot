import pytest
import grpc

import user_message_pb2_grpc as ums
import user_message_pb2 as um

channel = grpc.insecure_channel('frontend-service:50051')
stub = ums.UserMessageHandlerStub(channel)

def test_test():
    msg = um.UserMessage(
        user_id=1,
        text='/help'
    )
    responses = list(stub.HandleMessage(msg))
    assert len(responses) == 0
