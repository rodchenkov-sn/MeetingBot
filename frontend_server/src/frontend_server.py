from concurrent import futures

import grpc

import user_message_pb2 as um
import user_message_pb2_grpc as umg

import backend_service_pb2 as bs
import backend_service_pb2_grpc as bsg

channel = grpc.insecure_channel('localhost:50052')
stub = bsg.BackendServiceStub(channel)

states = dict()


class State:
    def __init__(self, command: str, action: str, value: int = None):
        self.command = command
        self.action = action
        self.value = value

    def to_str(self):
        value = ''
        if self.value is not None:
            value = f'__{self.value}'
        return f'{self.command}__{self.action}{value}'

    # def from_str(self, string: str):  # todo


class UserMessageHandler(umg.UserMessageHandlerServicer):
    def HandleMessage(self, request, context):
        user_id = request.user_id
        text = request.text
        print(f'\nuser_id: {user_id}')
        print(f'text: {text}')

        if text == '/create_team':
            set_state(user_id, State(command='create_team', action='enter_name'))
            yield um.ServerResponse(user_id=user_id, text='Enter team name')

        elif text == '/add_member':
            entity_id = bs.EntityId(id=user_id)
            named_infos = stub.GetOwnedTeams(entity_id)

            num_of_teams = 0
            for named_info in named_infos:
                yield um.ServerResponse(
                    user_id=user_id,
                    text=f'/add_member__{named_info.id} - add to \'{named_info.name}\' team')
                num_of_teams += 1
            set_state(user_id, State(command='add_member', action='choose_team'))

            if num_of_teams == 0:
                yield um.ServerResponse(user_id=user_id, text='You do not own any team')

        elif user_id in states:
            state = states[user_id]
            if state.command == 'create_team' and state.action == 'enter_name':
                create_team_message = bs.CreateTeamMsg(name=text, owner=user_id)
                entity_id = stub.CreateTeam(create_team_message)
                named_info = stub.GetTeamInfo(entity_id)
                team_name = named_info.name
                remove_state(user_id)
                yield um.ServerResponse(user_id=user_id, text=f'Team \'{team_name}\' created')

        else:
            yield um.ServerResponse(user_id=user_id, text='Sorry, bot does not understand you')


def set_state(user_id, state: State):
    states[user_id] = state
    print(f'Set state (user_id: {user_id}, state: {state.command}__{state.action}__{state.value})')


def remove_state(user_id):
    state = states[user_id]
    print(f'Remove state (user_id: {user_id}, state: {state.command}__{state.action}__{state.value})')
    del states[user_id]


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    umg.add_UserMessageHandlerServicer_to_server(UserMessageHandler(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    server.wait_for_termination()
