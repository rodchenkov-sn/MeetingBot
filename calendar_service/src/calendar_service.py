import grpc

from concurrent import futures
from datetime import datetime, timedelta

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

import calendar_service_pb2 as cs
import calendar_service_pb2_grpc as css


SCOPES = ['https://www.googleapis.com/auth/calendar']


active_flows = {}

active_services = {}


class CalendarServiceHandler(css.CalendarServiceServicer):
    def RequestAuth(self, request, context):
        user_id = request.user_id
        active_flows[user_id] = Flow.from_client_secrets_file(
            'credentials.json', SCOPES, redirect_uri='urn:ietf:wg:oauth:2.0:oob'
        )
        auth_url, _ = active_flows[user_id].authorization_url(prompt='consent')
        return cs.AuthUrl(user_id=user_id, auth_url=auth_url)

    def FinishAuth(self, request, context):
        user_id = request.user_id
        auth_code = request.auth_code
        if not user_id in active_flows:
            return cs.AuthStatus(user_id=user_id, ok=False)
        active_flows[user_id].fetch_token(code=auth_code)
        creds = active_flows[user_id].credentials
        active_services[user_id] = build('calendar', 'v3', credentials=creds)
        active_flows.pop(user_id)
        return cs.AuthStatus(user_id=user_id, ok=True)

    def PushEvent(self, request, context):
        uid = request.user_id
        start_time = request.time
        dt = datetime.now()
        start_time_s = dt.strftime('%Y-%m-%dT%H:%M:00')
        dt += timedelta(hours=1)
        end_time_s = dt.strftime('%Y-%m-%dT%H:%M:00')
        if not uid in active_services:
            return cs.EventAdded(added=False)
        event_obj = {
            'summary': request.desc,
            'start': { 'dateTime': start_time_s, 'timeZone': 'GMT+3' },
            'end': {'dateTime': end_time_s, 'timeZone': 'GMT+3' }
        }
        event = active_services[uid].events().insert(calendarId='primary', body=event_obj).execute()
        return cs.EventAdded(added=True)
        


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    css.add_CalendarServiceServicer_to_server(CalendarServiceHandler(), server)
    server.add_insecure_port('[::]:50053')
    server.start()
    server.wait_for_termination()
