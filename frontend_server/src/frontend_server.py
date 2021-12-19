from concurrent import futures
from dataclasses import dataclass

import grpc
import yaml

import user_message_pb2 as um
import user_message_pb2_grpc as ums

with open('config.yml', 'r') as config_file:
    config = yaml.safe_load(config_file)

states = dict()


@dataclass
class State:
    command: str
    action: str
    value: int = None


class UserMessageHandler(ums.UserMessageHandlerServicer):
    def HandleMessage(self, request, context):
        user_id = request.user_id
        text = request.text
        print(f'\nuser_id: {user_id}')
        print(f'text: {text}')

        if text == '/create_team':
            set_state(user_id, 'create_team:enter_name')
            yield um.ServerResponse(
                user_id=user_id,
                text='Enter name'
            )
        elif user_id in states and states[user_id] == 'create_team:enter_name':
            # todo Backend.CreateTeam
            remove_state(user_id)
            yield um.ServerResponse(
                user_id=user_id,
                text=f'Team {text} created'
            )
        else:
            yield um.ServerResponse(
                user_id=user_id,
                text='Sorry, bot does not understand you'
            )


def set_state(user_id, state):
    states[user_id] = state
    print(f'Set state (user_id: {user_id}, state: {states[user_id]})')


def remove_state(user_id):
    print(f'Remove state (user_id: {user_id}, state: {states[user_id]})')
    del states[user_id]


def state_to_str(state: State):
    value = ''
    if state.value is not None:
        value = f':{state.value}'
    return f'{state.command}:{state.action}{value}'


def str_to_state(string: str):
    # todo
    return State('', '')


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    ums.add_UserMessageHandlerServicer_to_server(UserMessageHandler(), server)
    server.add_insecure_port(config['frontend_server_url'])
    server.start()
    server.wait_for_termination()