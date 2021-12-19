from concurrent import futures

import grpc
import re

import user_message_pb2 as um
import user_message_pb2_grpc as umg

import backend_service_pb2 as bs
import backend_service_pb2_grpc as bsg

channel = grpc.insecure_channel('localhost:50052')
stub = bsg.BackendServiceStub(channel)

states = dict()


class State:
    def __init__(self, command: str, action: str, value: int = None):
        self.action = command
        self.sub_action = action
        self.value = value

    def to_str(self):
        value = ''
        if self.value is not None:
            value = f'__{self.value}'
        return f'{self.action}__{self.sub_action}{value}'


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
            state = get_state(user_id)

            if state.action == 'create_team' and state.sub_action == 'enter_name':
                create_team_message = bs.CreateTeamMsg(name=text, owner=user_id)
                entity_id = stub.CreateTeam(create_team_message)
                named_info = stub.GetTeamInfo(entity_id)
                team_name = named_info.name
                remove_state(user_id)
                yield um.ServerResponse(user_id=user_id, text=f'Team \'{team_name}\' created')

            elif state.action == 'add_member' and state.sub_action == 'choose_team':
                parts = re.split(r'__', text)
                if parts[0] == '/add_member':
                    try:
                        chosen_team_id = int(parts[1])
                    except ValueError:
                        yield um.ServerResponse(user_id=user_id, text='Team id should be number')
                    else:
                        yield um.ServerResponse(user_id=user_id, text='Tag person to add')
                        set_state(user_id, State(command='add_member', action='tag_member', value=chosen_team_id))

            elif state.action == 'add_member' and state.sub_action == 'tag_member':
                text = re.sub(r'\[', '', text)
                text = re.sub(r']', '', text)
                try:
                    tagged_user_id = int(text)
                except ValueError:
                    yield um.ServerResponse(user_id=user_id, text='Tag person again, please')
                else:
                    state = get_state(user_id)
                    team_id = state.value
                    entity_id = bs.EntityId(id=team_id)
                    named_info = stub.GetTeamInfo(entity_id)
                    team_name = named_info.name

                    remove_state(user_id)
                    yield um.ServerResponse(user_id=user_id, text='Invitation sent')

                    set_state(tagged_user_id, State(command='invited_to_team', action='accept_decline', value=team_id))
                    yield um.ServerResponse(user_id=tagged_user_id, text=f'You were invited to team \'{team_name}\'')
                    yield um.ServerResponse(user_id=tagged_user_id, text=f'/accept__{team_id}')
                    yield um.ServerResponse(user_id=tagged_user_id, text=f'/decline__{team_id}')

            elif state.action == 'invited_to_team' and state.sub_action == 'accept_decline':
                parts = re.split(r'__', text)
                if parts[0] == '/accept':
                    try:
                        invited_team_id = int(parts[1])
                    except ValueError:
                        yield um.ServerResponse(user_id=user_id, text='Team id should be number')
                    else:
                        participating = bs.Participating(object=invited_team_id, subject=user_id)
                        simple_response = stub.AddTeamMember(participating)
                        if simple_response.ok:
                            yield um.ServerResponse(user_id=user_id,
                                                    text=f'You were added to team \'{invited_team_id}\'')
                            remove_state(user_id)
                        else:
                            yield um.ServerResponse(user_id=user_id,
                                                    text=f'You were not added to team \'{invited_team_id}\'')

                elif parts[0] == '/decline':
                    try:
                        invited_team_id = int(parts[1])
                    except ValueError:
                        yield um.ServerResponse(user_id=user_id, text='Team id should be number')
                    else:
                        yield um.ServerResponse(user_id=user_id,
                                                text=f'You declined to join team \'{invited_team_id}\'')
                        remove_state(user_id)

        else:
            yield um.ServerResponse(user_id=user_id, text='Sorry, bot does not understand you')


def set_state(user_id, state: State):
    states[user_id] = state
    print(f'Set state (user_id: {user_id}, state: {state.action}__{state.sub_action}__{state.value})')


def get_state(user_id):
    return states[user_id]


def remove_state(user_id):
    state = states[user_id]
    print(f'Remove state (user_id: {user_id}, state: {state.action}__{state.sub_action}__{state.value})')
    del states[user_id]


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    umg.add_UserMessageHandlerServicer_to_server(UserMessageHandler(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    server.wait_for_termination()
