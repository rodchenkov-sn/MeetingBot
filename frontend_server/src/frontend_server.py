from concurrent import futures

import grpc

import user_message_pb2 as um
import user_message_pb2_grpc as ums

import localized_string_pb2 as ls
import localized_string_pb2_grpc as lss


class UserMessageHandler(ums.UserMessageHandlerServicer):
    def HandleMessage(self, request, context):
        print(get_localized_string(1))
        if request.text != "":
            yield um.ServerResponse(user_id=request.user_id, text=request.text)
        elif request.document.file_name != "":
            yield um.ServerResponse(user_id=request.user_id, text=request.document.file_name)


def get_localized_string(string_id):
    channel = grpc.insecure_channel('localhost:8000')
    stub = lss.LocalizationHandlerStub(channel)
    response = stub.getString(ls.StringRequest(string_id=string_id))
    return response.value


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    ums.add_UserMessageHandlerServicer_to_server(UserMessageHandler(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    server.wait_for_termination()
