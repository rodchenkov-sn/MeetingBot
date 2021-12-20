from concurrent import futures

import grpc
import re
from datetime import datetime

from typing import List

import user_message_pb2 as um
import user_message_pb2_grpc as umg

import backend_service_pb2 as bs
import backend_service_pb2_grpc as bsg

channel = grpc.insecure_channel('localhost:50052')
stub = bsg.BackendServiceStub(channel)


from states import State, StateRepo
from request_handler import RequestHandler
from command_handler import CommandHandlers
from states_handler import StatesHandlers


stateRepo = StateRepo()


def get_help_message(uid: int) -> um.ServerResponse:
    return um.ServerResponse(user_id=uid, text='/create_team to add team\n/invite_member to invite user\n/create_meeting to create meeting\n/invite_to_meeting to invite to meeting\n/add_daughter_team to add daughter team\n\n/help to see this message')


class StartCmdHandler(RequestHandler):
    def handle_request(self, request) -> List[um.ServerResponse]:
        return [
            get_help_message(request.user_id)
        ]


class CreateTeamCmdHandler(RequestHandler):
    def handle_request(self, request) -> List[um.ServerResponse]:
        uid = request.user_id
        text = request.text
        state = stateRepo.get_state(uid)
        if state is not None and state.action == 'creating_team':
            stateRepo.clear_state(uid)
            stub.CreateTeam(bs.CreateTeamMsg(name=text, owner=uid))
            return [
                um.ServerResponse(user_id=uid, text=f'team {text} created!'),
                get_help_message(uid)
            ]
        stateRepo.set_state(uid, State('creating_team', -1))
        return [
            um.ServerResponse(user_id=uid, text='Enter name:')
        ]


class InviteUserCmdHandler(RequestHandler):
    def handle_request(self, request) -> List[um.ServerResponse]:
        uid = request.user_id
        text = request.text
        state = stateRepo.get_state(uid)
        if request.text == '/invite_member':
            msg = ''
            teams = stub.GetOwnedTeams(bs.EntityId(id=uid))
            for team in teams:
                msg += f'/invite_member{team.id} -- to {team.name}\n'
            return [
                um.ServerResponse(user_id=uid, text=msg)
            ]
        elif state is None:
            group_id = int(text[14:])
            stateRepo.set_state(uid, State('inviting_members', group_id))
            return [
                um.ServerResponse(user_id=uid, text='Tag one or multiple users')
            ]
        else:
            group_id = state.argument
            stateRepo.clear_state(uid)
            mentioned_users = map(lambda m: int(m[2:len(m)-2]), re.findall(r'\[\[\d+\]\]', text))
            invite_msg = f'You were invited to team {stub.GetTeamInfo(bs.EntityId(id=group_id)).name} by [[{uid}]]\n\n/accept_invite{group_id} -- accept\n/reject_invite{group_id} -- reject'
            response = [um.ServerResponse(user_id=mid, text=invite_msg) for mid in mentioned_users]
            response.append(um.ServerResponse(user_id=uid, text='Invitations were send'))
            response.append(get_help_message(uid))
            return response


class InviteReactionCmdHandler(RequestHandler):
    def handle_request(self, request) -> List[um.ServerResponse]:
        uid = request.user_id
        text = request.text
        group_id = int(text[14:])
        owner_id = stub.GetGroupOwner(bs.EntityId(id=group_id)).id
        if text.startswith('/accept_invite'):
            stub.AddTeamMember(bs.Participating(object=group_id, subject=uid))
            return [
                um.ServerResponse(user_id=uid, text='Wellcome to the club buddy'),
                um.ServerResponse(user_id=owner_id, text=f'[[{uid}]] is now your slave')
            ]
        else:
            return [
                um.ServerResponse(user_id=uid, text='Oh fuck you!'),
                um.ServerResponse(user_id=owner_id, text=f'[[{uid}]] rejected the invitation')
            ]


class CreateMeetingCmdHandler(RequestHandler):
    def handle_request(self, request) -> List[um.ServerResponse]:
        uid = request.user_id
        text = request.text
        state = stateRepo.get_state(uid)
        if text == '/create_meeting':
            msg = ''
            teams = stub.GetGroupsToCreateMeeting(bs.EntityId(id=uid))
            for team in teams:
                msg += f'/create_meeting{team.id} -- in {team.name}\n'
            return [
                um.ServerResponse(user_id=uid, text=msg)
            ]
        elif state is None:
            group_id = int(text[15:])
            meeting_id = stub.CreateMeeting(bs.MeetingInfo(
                id=-1,
                creator=uid,
                team=group_id,
                desc='',
                time=-1
            )).id
            stateRepo.set_state(uid, State('setting_meeting_desc', meeting_id, _arg2=group_id))
            return [
                um.ServerResponse(user_id=uid, text='Enter description:')
            ]
        elif state.action == 'setting_meeting_desc':
            meeting_id = state.argument
            stateRepo.set_state(uid, State('setting_meeting_time', state.argument, _arg2=state.argument2))
            stub.UpdateMeetingInfo(bs.MeetingInfo(
                id=meeting_id,
                creator=-1, #not important
                team=-1, # not important
                desc=text,
                time=-1
            ))
            return [ 
                um.ServerResponse(user_id=uid, text='Enter datetime (in format DD-MM-YYYY HH:MM):')
            ]
        elif state.action == 'setting_meeting_time':
            meeting_id = state.argument
            group_id = state.argument2
            stateRepo.clear_state(uid)
            dt = datetime.strptime(text, '%d-%m-%Y %H:%M')
            stub.UpdateMeetingInfo(bs.MeetingInfo(
                id=meeting_id,
                creator=-1, #not important
                team=-1, # not important
                desc='', # not important
                time=int(dt.timestamp())
            ))
            group_owner = stub.GetGroupOwner(bs.EntityId(id=group_id)).id
            group_policy = stub.GetGroupPolicy(bs.EntityId(id=group_id))
            if uid == group_owner or not group_policy.needApproveForMeetingCreation:
                stub.ApproveMeeting(bs.EntityId(id=meeting_id))
                return [ 
                    um.ServerResponse(user_id=uid, text=f'Meeting created!')
                ]
            else:
                meeting_info = stub.GetMeetingInfo(bs.EntityId(id=meeting_id))
                return [
                    um.ServerResponse(user_id=uid, text='Meeting will be approved by the group owner. Just relax and wait'),
                    um.ServerResponse(user_id=group_owner, text=f'User [[{uid}]] created meeting {meeting_info.desc}\n/approve_meeting{meeting_id} -- approve\n/reject_meeting{meeting_id} -- reject')
                ]


class MeetingApproveCmdHandle(RequestHandler):
    def handle_request(self, request) -> List[um.ServerResponse]:
        uid = request.user_id
        text = request.text
        if text.startswith('/approve_meeting'):
            meeting_id = int(text[16:])
            stub.ApproveMeeting(bs.EntityId(id=meeting_id))
            meeting_info = stub.GetMeetingInfo(bs.EntityId(id=meeting_id))
            return [
                um.ServerResponse(user_id=uid, text='Approved!'),
                um.ServerResponse(user_id=meeting_info.creator, text=f'Meeting {meeting_info.desc} was approved')
            ]
        else:
            meeting_id = int(text[15:])
            meeting_info = stub.GetMeetingInfo(bs.EntityId(id=meeting_id))
            return [
                um.ServerResponse(user_id=uid, text='Rejected!'),
                um.ServerResponse(user_id=meeting_info.creator, text=f'Meeting {meeting_info.desc} was rejected')
            ]


# todo: test
class InviteToMeetingCmdHandler(RequestHandler):
    def handle_request(self, request) -> List[um.ServerResponse]:
        uid = request.user_id
        text = request.text
        state = stateRepo.get_state(uid)
        if request.text == '/invite_to_meeting':
            msg = ''
            meetings = stub.GetOwnedMeetings(bs.EntityId(id=uid))
            for meeting in meetings:
                msg += f'/invite_to_meeting{meeting.id} -- to {meeting.name}'
            return [
                um.ServerResponse(user_id=uid, text=msg)
            ]
        elif state is None:
            meeting_id = int(text[18:])
            stateRepo.set_state(uid, State('inviting_to_meeting', meeting_id))
            return [
                um.ServerResponse(user_id=uid, text='Tag one or multiple users')
            ]
        else:
            meeting_id = state.argument
            stateRepo.clear_state(uid)
            mentioned_users = map(lambda m: int(m[2:len(m) - 2]), re.findall(r'\[\[\d+\]\]', text))
            # fixme: invitable_members is empty (i have only one tg account)
            invitable_members = map(lambda x: x.id, stub.GetInvitableMembers(bs.EntityId(id=uid)))
            invite_msg = f'You were invited to meeting {stub.GetMeetingInfo(bs.EntityId(id=meeting_id)).desc} by [[{uid}]]\n\n/accept_meeting_invite{meeting_id} -- accept\n/reject_meeting_invite{meeting_id} -- reject'
            response = [um.ServerResponse(user_id=mu, text=invite_msg) for mu in mentioned_users if mu in invitable_members]
            response.append(um.ServerResponse(user_id=uid, text='Invitations to meeting were send'))
            response.append(get_help_message(uid))
            return response


# todo: test
class MeetingInviteReactionCmdHandler(RequestHandler):
    def handle_request(self, request) -> List[um.ServerResponse]:
        uid = request.user_id
        text = request.text
        meeting_id = int(text[22:])
        meeting_info = stub.GetMeetingInfo(bs.EntityId(id=meeting_id))
        creator_id = meeting_info.id
        if text.startswith('/accept_meeting_invite'):
            stub.AddParticipant(bs.Participating(object=meeting_id, subject=uid))
            return [
                um.ServerResponse(user_id=uid, text='You accepted meeting invitation'),
                um.ServerResponse(user_id=uid, text=f'Meeting {meeting_info.desc} starts in 5 minutes', event_id=meeting_id, timestamp=300),
                um.ServerResponse(user_id=creator_id, text=f'[[{uid}]] accepted meeting invitation')
            ]
        else:
            return [
                um.ServerResponse(user_id=uid, text='You rejected meeting invitation'),
                um.ServerResponse(user_id=creator_id, text=f'[[{uid}]] rejected meeting invitation')
            ]


class AddDaughterTeamCmdHandler(RequestHandler):
    def handle_request(self, request) -> List[um.ServerResponse]:
        uid = request.user_id
        text = request.text
        state = stateRepo.get_state(uid)
        if text == '/add_daughter_team':
            msg = ''
            teams = stub.GetOwnedTeams(bs.EntityId(id=uid))
            for team in teams:
                msg += f'/add_daughter_team{team.id} -- add daughter team to {team.name}\n'
            return [
                um.ServerResponse(user_id=uid, text=msg)
            ]
        elif state is None:
            parent_team_id = int(text[18:])
            stateRepo.set_state(uid, State('adding_daughter_team', parent_team_id))
            return [
                um.ServerResponse(user_id=uid, text='Enter daughter team id:')
            ]
        else:
            parent_team_id = state.argument
            stateRepo.clear_state(uid)
            daughter_team_id = int(text)
            stub.AddParentTeam(bs.Participating(object=parent_team_id, subject=daughter_team_id))
            parent_team_name = stub.GetTeamInfo(bs.EntityId(id=parent_team_id)).name
            daughter_team_name = stub.GetTeamInfo(bs.EntityId(id=daughter_team_id)).name
            response = [um.ServerResponse(user_id=uid, text=f'{daughter_team_name} team is now a daughter of {parent_team_name} team')]
            response.append(get_help_message(uid))
            return response


commandHandlers = CommandHandlers({
    '/start': StartCmdHandler(),
    '/help': StartCmdHandler(),
    '/create_team': CreateTeamCmdHandler(),
    '/invite_member': InviteUserCmdHandler(),
    '/accept_invite': InviteReactionCmdHandler(),
    '/reject_invite': InviteReactionCmdHandler(),
    '/create_meeting': CreateMeetingCmdHandler(),
    '/approve_meeting': MeetingApproveCmdHandle(),
    '/reject_meeting': MeetingApproveCmdHandle(),
    '/invite_to_meeting': InviteToMeetingCmdHandler(),
    '/accept_meeting_invite': MeetingInviteReactionCmdHandler(),
    '/reject_meeting_invite': MeetingInviteReactionCmdHandler(),
    '/add_daughter_team': AddDaughterTeamCmdHandler()
})

statesHandlers = StatesHandlers({
    'creating_team': CreateTeamCmdHandler(),
    'inviting_members': InviteUserCmdHandler(),
    'setting_meeting_desc': CreateMeetingCmdHandler(),
    'setting_meeting_time': CreateMeetingCmdHandler(),
    'inviting_to_meeting': InviteToMeetingCmdHandler(),
    'adding_daughter_team': AddDaughterTeamCmdHandler()
})


class UserMessageHandler(umg.UserMessageHandlerServicer):
    def HandleMessage(self, request, context):
        responses = commandHandlers.try_handle(request)
        if responses is None:
            responses = statesHandlers.try_handle(request, stateRepo.get_state(request.user_id))
        if responses is None:
            responses = [get_help_message(request.user_id)]
        for response in responses:
            yield response
        

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    umg.add_UserMessageHandlerServicer_to_server(UserMessageHandler(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    server.wait_for_termination()
