import grpc

from concurrent import futures

import calendar_service_pb2 as cs
import calendar_service_pb2_grpc as css


class CalendarServiceHandler(css.CalendarServiceServicer):
    def RequestAuth(self, request, context):
        user_id = request.user_id
        return cs.AuthUrl(user_id=user_id, auth_url='https://test_auth_url.org')

    def FinishAuth(self, request, context):
        user_id = request.user_id
        return cs.AuthStatus(user_id=user_id, ok=True)

    def PushEvent(self, request, context):
        return cs.EventAdded(added=True)
        

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    css.add_CalendarServiceServicer_to_server(CalendarServiceHandler(), server)
    server.add_insecure_port('[::]:50053')
    server.start()
    server.wait_for_termination()
