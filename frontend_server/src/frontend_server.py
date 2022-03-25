from concurrent import futures
from os import stat

import grpc
import re
from datetime import datetime, timedelta

from typing import List

import user_message_pb2 as um
import user_message_pb2_grpc as umg

import backend_service_pb2 as bs
import backend_service_pb2_grpc as bsg

import calendar_service_pb2 as cs
import calendar_service_pb2_grpc as css

import file_repo_service_pb2 as fs
import file_repo_service_pb2_grpc as fss

from states import State, StateRepo
from request_handler import RequestHandler
from command_handler import CommandHandlers
from states_handler import StatesHandlers

from lines import LinesRepo


def get_help_message(uid: int, line_repo) -> um.ServerResponse:
    msg = ''
    help_create_team = line_repo.get_line('help_create_team', uid)
    msg += f'/create_team - {help_create_team}\n'
    help_invite_member = line_repo.get_line('help_invite_member', uid)
    msg += f'/invite_member - {help_invite_member}\n'
    help_create_meeting = line_repo.get_line('help_create_meeting', uid)
    msg += f'/create_meeting - {help_create_meeting}\n'
    help_invite_to_meeting = line_repo.get_line('help_invite_to_meeting', uid)
    msg += f'/invite_to_meeting - {help_invite_to_meeting}\n'
    help_add_daughter_team = line_repo.get_line('help_add_daughter_team', uid)
    msg += f'/add_child_team - {help_add_daughter_team}\n'
    help_edit_policy = line_repo.get_line('help_edit_policy', uid)
    msg += f'/edit_policy - {help_edit_policy}\n'
    help_add_to_meeting = line_repo.get_line('help_add_to_meeting', uid)
    msg += f'/add_to_meeting - {help_add_to_meeting}\n'
    help_update_meeting_time = line_repo.get_line('help_update_meeting_time', uid)
    msg += f'/update_meeting_time - {help_update_meeting_time}\n'
    help_get_agenda = line_repo.get_line('help_get_agenda', uid)
    msg += f'/get_agenda - {help_get_agenda}\n'
    help_upload_file = line_repo.get_line('help_upload_file', uid)
    msg += f'/upload_file - {help_upload_file}\n'
    help_get_files = line_repo.get_line('help_get_files', uid)
    msg += f'/get_files - {help_get_files}\n'
    help_auth_gcal = line_repo.get_line('help_auth_gcal', uid)
    msg += f'/auth_gcal - {help_auth_gcal}\n'
    help_change_language = line_repo.get_line('help_change_language', uid)
    msg += f'/change_language - {help_change_language}\n'
    help_help = line_repo.get_line('help_help', uid)
    msg += f'\n/help - {help_help}'
    return um.ServerResponse(user_id=uid, text=msg)
                             

class StartCmdHandler(RequestHandler):
    def __init__(self, lines):
        super().__init__()
        self.__lines = lines

    def handle_request(self, request) -> List[um.ServerResponse]:
        return [
            get_help_message(request.user_id, self.__lines)
        ]


class CreateTeamCmdHandler(RequestHandler):
    def __init__(self, states, backend, lines):
        super().__init__()
        self.__states = states
        self.__backend = backend
        self.__lines = lines

    def handle_request(self, request) -> List[um.ServerResponse]:
        uid = request.user_id
        text = request.text
        state = self.__states.get_state(uid)
        if state is not None and state.action == 'creating_team':
            self.__states.clear_state(uid)
            self.__backend.CreateTeam(bs.CreateTeamMsg(name=text, owner=uid))
            create_team_team_created = self.__lines.get_line('create_team_team_created', uid)
            return [
                um.ServerResponse(user_id=uid, text=f'{text} {create_team_team_created}!'),
                get_help_message(uid, self.__lines)
            ]
        self.__states.set_state(uid, State('creating_team', -1))
        create_team_enter_name = self.__lines.get_line('create_team_enter_name', uid)
        return [
            um.ServerResponse(user_id=uid, text=f'{create_team_enter_name}:')
        ]


class InviteUserCmdHandler(RequestHandler):
    def __init__(self, states, backend, lines):
        super().__init__()
        self.__states = states
        self.__backend = backend
        self.__lines = lines

    def handle_request(self, request) -> List[um.ServerResponse]:
        uid = request.user_id
        text = request.text
        state = self.__states.get_state(uid)
        if request.text == '/invite_member':
            response = []
            teams = self.__backend.GetOwnedTeams(bs.EntityId(id=uid))
            for team in teams:
                response.append(um.ServerResponse(user_id=uid, text=f'/invite_member{team.id} -- {team.name}\n'))
            return response
        elif state is None:
            group_id = int(text[14:])
            self.__states.set_state(uid, State('inviting_members', group_id))
            invite_user_tag_users = self.__lines.get_line('invite_user_tag_users', uid)
            return [
                um.ServerResponse(user_id=uid, text=f'{invite_user_tag_users}')
            ]
        else:
            group_id = state.argument
            self.__states.clear_state(uid)
            mentioned_users = map(lambda m: int(m[2:len(m) - 2]), re.findall(r'\[\[\d+\]\]', text))
            response = []
            for mid in mentioned_users:
                invite_user_you_were_invited = self.__lines.get_line('invite_user_you_were_invited', mid)
                invite_user_by = self.__lines.get_line('invite_user_by', mid)
                invite_user_accept = self.__lines.get_line('invite_user_accept', mid)
                invite_user_reject = self.__lines.get_line('invite_user_reject', mid)
                invite_msg = f'{invite_user_you_were_invited} {self.__backend.GetTeamInfo(bs.EntityId(id=group_id)).name} {invite_user_by} [[{uid}]]\n\n/accept_invite{group_id} -- {invite_user_accept}\n/reject_invite{group_id} -- {invite_user_reject}'
                response.append(um.ServerResponse(user_id=mid, text=invite_msg))
            invite_user_invitations_send = self.__lines.get_line('invite_user_invitations_send', uid)
            response.append(um.ServerResponse(user_id=uid, text=f'{invite_user_invitations_send}'))
            response.append(get_help_message(uid, self.__lines))
            return response


class InviteReactionCmdHandler(RequestHandler):
    def __init__(self, states, backend, lines):
        super().__init__()
        self.__states = states
        self.__backend = backend
        self.__lines = lines

    def handle_request(self, request) -> List[um.ServerResponse]:
        uid = request.user_id
        text = request.text
        group_id = int(text[14:])
        owner_id = self.__backend.GetGroupOwner(bs.EntityId(id=group_id)).id
        if text.startswith('/accept_invite'):
            self.__backend.AddTeamMember(bs.Participating(object=group_id, subject=uid))
            invite_reaction_accepted = self.__lines.get_line('invite_reaction_accepted', uid)
            invite_reaction_accepted_invitation = self.__lines.get_line('invite_reaction_accepted_invitation', owner_id)
            return [
                um.ServerResponse(user_id=uid, text=f'{invite_reaction_accepted}!'),
                um.ServerResponse(user_id=owner_id, text=f'[[{uid}]] {invite_reaction_accepted_invitation}')
            ]
        else:
            invite_reaction_rejected = self.__lines.get_line('invite_reaction_rejected', uid)
            invite_reaction_rejected_invitation = self.__lines.get_line('invite_reaction_rejected_invitation', owner_id)
            return [
                um.ServerResponse(user_id=uid, text=f'{invite_reaction_rejected}!'),
                um.ServerResponse(user_id=owner_id, text=f'[[{uid}]] {invite_reaction_rejected_invitation}')
            ]


class CreateMeetingCmdHandler(RequestHandler):
    def __init__(self, states, backend, lines):
        super().__init__()
        self.__states = states
        self.__backend = backend
        self.__lines = lines

    def handle_request(self, request) -> List[um.ServerResponse]:
        uid = request.user_id
        text = request.text
        state = self.__states.get_state(uid)
        if text == '/create_meeting':
            msg = ''
            teams = self.__backend.GetGroupsToCreateMeeting(bs.EntityId(id=uid))
            for team in teams:
                msg += f'/create_meeting{team.id} -- {team.name}\n'
            return [
                um.ServerResponse(user_id=uid, text=msg)
            ]
        elif state is None:
            group_id = int(text[15:])
            meeting_id = self.__backend.CreateMeeting(bs.MeetingInfo(
                id=-1,
                creator=uid,
                team=group_id,
                desc='',
                time=-1
            )).id
            self.__states.set_state(uid, State('setting_meeting_desc', meeting_id, _arg2=group_id))
            create_meeting_enter_description = self.__lines.get_line('create_meeting_enter_description', uid)
            return [
                um.ServerResponse(user_id=uid, text=f'{create_meeting_enter_description}:')
            ]
        elif state.action == 'setting_meeting_desc':
            meeting_id = state.argument
            self.__states.set_state(uid, State('setting_meeting_time', state.argument, _arg2=state.argument2))
            self.__backend.UpdateMeetingInfo(bs.MeetingInfo(
                id=meeting_id,
                creator=-1,  # not important
                team=-1,  # not important
                desc=text,
                time=-1
            ))
            create_meeting_enter_datetime = self.__lines.get_line('create_meeting_enter_datetime', uid)
            return [
                um.ServerResponse(user_id=uid, text=f'{create_meeting_enter_datetime}:')
            ]
        elif state.action == 'setting_meeting_time':
            meeting_id = state.argument
            group_id = state.argument2
            try:
                dt = datetime.strptime(text, '%d-%m-%Y %H:%M')
            except:
                return [
                    um.ServerResponse(user_id=uid, text=f'try again!')
                ]
            self.__states.clear_state(uid)
            self.__backend.UpdateMeetingInfo(bs.MeetingInfo(
                id=meeting_id,
                creator=-1,  # not important
                team=-1,  # not important
                desc='',  # not important
                time=int(dt.timestamp())
            ))
            group_owner = self.__backend.GetGroupOwner(bs.EntityId(id=group_id)).id
            group_policy = self.__backend.GetGroupPolicy(bs.EntityId(id=group_id))
            if uid == group_owner or not group_policy.needApproveForMeetingCreation:
                self.__backend.ApproveMeeting(bs.EntityId(id=meeting_id))
                create_meeting_meeting_created = self.__lines.get_line('create_meeting_meeting_created', uid)
                ret = [
                    um.ServerResponse(user_id=uid, text=f'{create_meeting_meeting_created}!')
                ]
                minfo = self.__backend.GetMeetingInfo(bs.EntityId(id=meeting_id))
                ret.append(um.ServerResponse(user_id=uid, text=f'{minfo.desc} in T - 5!', event_id=meeting_id, timestamp=int((dt - timedelta(minutes=5)).timestamp())))
            else:
                meeting_info = self.__backend.GetMeetingInfo(bs.EntityId(id=meeting_id))
                create_meeting_wait_approval = self.__lines.get_line('create_meeting_wait_approval', uid)
                create_meeting_user = self.__lines.get_line('create_meeting_user', group_owner)
                create_meeting_created_meeting = self.__lines.get_line('create_meeting_created_meeting', group_owner)
                create_meeting_approve = self.__lines.get_line('create_meeting_approve', group_owner)
                create_meeting_reject = self.__lines.get_line('create_meeting_reject', group_owner)
                ret = [
                    um.ServerResponse(user_id=uid, text=f'{create_meeting_wait_approval}'),
                    um.ServerResponse(user_id=group_owner, text=f'{create_meeting_user} [[{uid}]] {create_meeting_created_meeting} {meeting_info.desc}\n/approve_meeting{meeting_id} -- {create_meeting_approve}\n/reject_meeting{meeting_id} -- {create_meeting_reject}')
                ]
            return ret


class MeetingApproveCmdHandle(RequestHandler):
    def __init__(self, states, backend, lines):
        super().__init__()
        self.__states = states
        self.__backend = backend
        self.__lines = lines

    def handle_request(self, request) -> List[um.ServerResponse]:
        uid = request.user_id
        text = request.text
        if text.startswith('/approve_meeting'):
            meeting_id = int(text[16:])
            self.__backend.ApproveMeeting(bs.EntityId(id=meeting_id))
            meeting_info = self.__backend.GetMeetingInfo(bs.EntityId(id=meeting_id))
            meeting_approve_approved = self.__lines.get_line('meeting_approve_approved', uid)
            meeting_approve_meeting = self.__lines.get_line('meeting_approve_meeting', meeting_info.creator)
            meeting_approve_was_approved = self.__lines.get_line('meeting_approve_was_approved', meeting_info.creator)
            return [
                um.ServerResponse(user_id=uid, text=f'{meeting_approve_approved}!'),
                um.ServerResponse(user_id=meeting_info.creator, text=f'{meeting_approve_meeting} {meeting_info.desc} {meeting_approve_was_approved}')
            ]
        else:
            meeting_id = int(text[15:])
            meeting_info = self.__backend.GetMeetingInfo(bs.EntityId(id=meeting_id))
            meeting_approve_rejected = self.__lines.get_line('meeting_approve_rejected', uid)
            meeting_approve_meeting = self.__lines.get_line('meeting_approve_meeting', meeting_info.creator)
            meeting_approve_was_rejected = self.__lines.get_line('meeting_approve_was_rejected', meeting_info.creator)
            return [
                um.ServerResponse(user_id=uid, text=f'{meeting_approve_rejected}!'),
                um.ServerResponse(user_id=meeting_info.creator, text=f'{meeting_approve_meeting} {meeting_info.desc} {meeting_approve_was_rejected}')
            ]


class InviteToMeetingCmdHandler(RequestHandler):
    def __init__(self, states, backend, lines):
        super().__init__()
        self.__states = states
        self.__backend = backend
        self.__lines = lines

    def handle_request(self, request) -> List[um.ServerResponse]:
        uid = request.user_id
        text = request.text
        state = self.__states.get_state(uid)
        if request.text == '/invite_to_meeting':
            msg = ''
            meetings = self.__backend.GetOwnedMeetings(bs.EntityId(id=uid))
            for meeting in meetings:
                msg += f'/invite_to_meeting{meeting.id} -- {meeting.name}\n'
            return [
                um.ServerResponse(user_id=uid, text=msg)
            ]
        elif state is None:
            meeting_id = int(text[18:])
            self.__states.set_state(uid, State('inviting_to_meeting', meeting_id))
            inviting_to_meeting_tag = self.__lines.get_line('inviting_to_meeting_tag', uid)
            return [
                um.ServerResponse(user_id=uid, text=f'{inviting_to_meeting_tag}')
            ]
        else:
            meeting_id = state.argument
            self.__states.clear_state(uid)
            mentioned_users = map(lambda m: int(m[2:len(m) - 2]), re.findall(r'\[\[\d+\]\]', text))
            team_id = self.__backend.GetMeetingInfo(bs.EntityId(id=meeting_id)).team
            invitable_members = map(lambda x: x.id, self.__backend.GetInvitableMembers(bs.EntityId(id=team_id)))
            response = []
            noninvitable = []
            for mu in mentioned_users:
                if mu in invitable_members:
                    inviting_to_meeting_you_were_invited = self.__lines.get_line('inviting_to_meeting_you_were_invited', mu)
                    inviting_to_meeting_by = self.__lines.get_line('inviting_to_meeting_by', mu)
                    inviting_to_meeting_accept = self.__lines.get_line('inviting_to_meeting_accept', mu)
                    inviting_to_meeting_reject = self.__lines.get_line('inviting_to_meeting_reject', mu)
                    invite_msg = f'{inviting_to_meeting_you_were_invited} {self.__backend.GetMeetingInfo(bs.EntityId(id=meeting_id)).desc} {inviting_to_meeting_by} [[{uid}]]\n\n/accept_meeting_invite{meeting_id} -- {inviting_to_meeting_accept}\n/reject_meeting_invite{meeting_id} -- {inviting_to_meeting_reject}'
                    response.append(um.ServerResponse(user_id=mu, text=invite_msg))
                else:
                    noninvitable.append(mu)
            inviting_to_meeting_invitations_send = self.__lines.get_line('inviting_to_meeting_invitations_send', uid)
            response.append(um.ServerResponse(user_id=uid, text=f'{inviting_to_meeting_invitations_send}'))
            if len(noninvitable) > 0:
                response.append(um.ServerResponse(user_id=uid, text=f'cant invite:\n{" ".join(map(lambda x: f"[[{x}]]", noninvitable))}'))
            response.append(get_help_message(uid, self.__lines))
            return response


class MeetingInviteReactionCmdHandler(RequestHandler):
    def __init__(self, states, backend, lines):
        super().__init__()
        self.__states = states
        self.__backend = backend
        self.__lines = lines

    def handle_request(self, request) -> List[um.ServerResponse]:
        uid = request.user_id
        text = request.text
        meeting_id = int(text[22:])
        meeting_info = self.__backend.GetMeetingInfo(bs.EntityId(id=meeting_id))
        creator_id = meeting_info.creator
        if text.startswith('/accept_meeting_invite'):
            self.__backend.AddParticipant(bs.Participating(object=meeting_id, subject=uid))
            meeting_date = datetime.fromtimestamp(meeting_info.time)
            meeting_invite_reaction_you_accepted = self.__lines.get_line('meeting_invite_reaction_you_accepted', uid)
            meeting_invite_reaction_meeting_starts_at = self.__lines.get_line('meeting_invite_reaction_meeting_starts_at', uid)
            meeting_invite_reaction_accepted = self.__lines.get_line('meeting_invite_reaction_accepted', creator_id)
            minfo = self.__backend.GetMeetingInfo(bs.EntityId(id=meeting_id))
            return [
                um.ServerResponse(user_id=uid, text=f'{minfo.desc} in T - 5!\n\n/pom{meeting_id} -- heading!\n/aom{meeting_id} -- ignore', event_id=meeting_id, timestamp=int((datetime.fromtimestamp(minfo.time) - timedelta(minutes=5)).timestamp())),
                um.ServerResponse(user_id=uid, text=f'{meeting_invite_reaction_you_accepted}'),
                um.ServerResponse(user_id=uid, text=f'{meeting_info.desc} {meeting_invite_reaction_meeting_starts_at} {meeting_date}'),
                um.ServerResponse(user_id=creator_id, text=f'[[{uid}]] {meeting_invite_reaction_accepted}')
            ]
        else:
            meeting_invite_reaction_you_rejected = self.__lines.get_line('meeting_invite_reaction_you_rejected', uid)
            meeting_invite_reaction_rejected = self.__lines.get_line('meeting_invite_reaction_rejected', creator_id)
            return [
                um.ServerResponse(user_id=uid, text=f'{meeting_invite_reaction_you_rejected}'),
                um.ServerResponse(user_id=creator_id, text=f'[[{uid}]] {meeting_invite_reaction_rejected}')
            ]


class NotificationReactionCmdHandler(RequestHandler):
    def __init__(self, states, backend, lines):
        super().__init__()
        self.__states = states
        self.__backend = backend
        self.__lines = lines

    def handle_request(self, request) -> List[um.ServerResponse]:
        uid = request.user_id
        text = str(request.text)
        mid = int(text[4:])
        minfo = self.__backend.GetMeetingInfo(bs.EntityId(id=mid))
        ret = [um.ServerResponse(user_id=uid, text='Understandable have a nice day')]
        if text.startswith('/pom'):
            ret.append(um.ServerResponse(user_id=minfo.creator, text=f'[[{uid}]] id heading to {minfo.desc}'))
        else:
            ret.append(um.ServerResponse(user_id=minfo.creator, text=f'[[{uid}]] wont be at {minfo.desc}'))
        return ret


class AddDaughterTeamCmdHandler(RequestHandler):
    def __init__(self, states, backend, lines):
        super().__init__()
        self.__states = states
        self.__backend = backend
        self.__lines = lines

    def handle_request(self, request) -> List[um.ServerResponse]:
        uid = request.user_id
        text = str(request.text)
        state = self.__states.get_state(uid)
        if text == '/add_child_team':
            response = []
            teams = self.__backend.GetOwnedTeams(bs.EntityId(id=uid))
            add_daughter_team_add_to = self.__lines.get_line('add_daughter_team_add_to', uid)
            for team in teams:
                response.append(um.ServerResponse(user_id=uid, text=f'/add_child_team{team.id} -- {add_daughter_team_add_to} {team.name}\n'))
            return response
        elif text.startswith('/add_child_team') and state is None:
            parent_team_id = int(text[15:])
            self.__states.set_state(uid, State('searching_child_team', parent_team_id))
            return [
                um.ServerResponse(user_id=uid, text=f'mention team owner:')
            ]
        elif state is not None and state.action == 'searching_child_team':
            mentioned_users = list(map(lambda m: int(m[2:len(m) - 2]), re.findall(r'\[\[\d+\]\]', text)))
            response = []
            if len(mentioned_users) == 1:
                mus = mentioned_users[0]
                owned_teams = self.__backend.GetOwnedTeams(bs.EntityId(id=mus))
                for team in owned_teams:
                    response.append(um.ServerResponse(user_id=uid, text=f'/add_child_team{team.id} -- {team.name}\n'))
            else:
                return [um.ServerResponse(user_id=uid, text='mention only one user pls')]
            pid = state.argument
            self.__states.clear_state(uid)
            self.__states.set_state(uid, State('adding_child_team', pid, mus))
            return response
        elif state is not None and state.action == 'adding_child_team' and text.startswith('/add_child_team'):
            pid = state.argument
            oid = state.argument2
            self.__states.clear_state(uid)
            child_team_id = int(text[15:])
            ctinfo = self.__backend.GetTeamInfo(bs.EntityId(id=child_team_id))
            ptinfo = self.__backend.GetTeamInfo(bs.EntityId(id=pid))
            return [
                um.ServerResponse(user_id=uid, text='invitation was sent'),
                get_help_message(uid, self.__lines),
                um.ServerResponse(user_id=oid, text=f'[[{uid}]] wants to add {ctinfo.name} to {ptinfo.name} children\n\n/acc_child{ctinfo.id}_{ptinfo.id} -- accept\n/rej_child{ctinfo.id}_{ptinfo.id} -- reject')
            ]
        else:
            if state is not None:
                self.__states.clear_state(uid)
            return [um.ServerResponse(user_id=uid, text='something went wront')]


class AddChildTeamNotiifcationReactionCmdHandler(RequestHandler):
    def handle_request(self, request) -> List[um.ServerResponse]:
        return []
        # uid = request.user_id
        # text = str(request.text)
        # teams = text[10:].split('_')
        # cid = int(teams[0])
        # pid = int(teams[1])
        # oid = stub.GetGroupOwner(bs.EntityId(id=pid)).id
        # ret = [um.ServerResponse(user_id=uid, text='understandable')]
        # if text.startswith('/acc_child'):
        #     stub.AddParentTeam(bs.Participating(object=pid, subject=cid))
        #     ret.append(um.ServerResponse(user_id=oid, text=f'[[{uid}]] team is now your child'))
        # else:
        #     ret.append(um.ServerResponse(user_id=oid, text=f'[[{uid}]] rejected child invitation'))
        # return ret


class EditPolicyCmdHandler(RequestHandler):
    def __init__(self, states, backend, lines):
        super().__init__()
        self.__states = states
        self.__backend = backend
        self.__lines = lines

    def handle_request(self, request) -> List[um.ServerResponse]:
        uid = request.user_id
        text = request.text
        state = self.__states.get_state(uid)
        if text == '/edit_policy':
            response = []
            teams = self.__backend.GetOwnedTeams(bs.EntityId(id=uid))
            edit_policy_edit_of = self.__lines.get_line('edit_policy_edit_of', uid)
            for team in teams:
                response.append(um.ServerResponse(user_id=uid, text=f'/edit_policy{team.id} -- {edit_policy_edit_of} {team.name}\n'))
            return response
        elif state is None:
            team_id = int(text[12:])
            self.__states.set_state(uid, State('editing_policy', team_id))
            group_policy = self.__backend.GetGroupPolicy(bs.EntityId(id=team_id))
            edit_policy_enter_one_zero = self.__lines.get_line('edit_policy_enter_one_zero', uid)
            edit_policy_allow_meetings = self.__lines.get_line('edit_policy_allow_meetings', uid)
            edit_policy_need_approve = self.__lines.get_line('edit_policy_need_approve', uid)
            edit_policy_propagate_policy = self.__lines.get_line('edit_policy_propagate_policy', uid)
            edit_policy_parent_visible = self.__lines.get_line('edit_policy_parent_visible', uid)
            edit_policy_propagate_admin = self.__lines.get_line('edit_policy_propagate_admin', uid)
            return [
                um.ServerResponse(user_id=uid, text=f'{edit_policy_enter_one_zero}:'),
                um.ServerResponse(user_id=uid, text=f'\n1. {edit_policy_allow_meetings}: {group_policy.allowUsersToCreateMeetings}'),
                um.ServerResponse(user_id=uid, text=f'\n2. {edit_policy_need_approve}: {group_policy.needApproveForMeetingCreation}'),
                um.ServerResponse(user_id=uid, text=f'\n3. {edit_policy_propagate_policy}: {group_policy.propagatePolicy}'),
                um.ServerResponse(user_id=uid, text=f'\n4. {edit_policy_parent_visible}: {group_policy.parentVisible}'),
                um.ServerResponse(user_id=uid, text=f'\n5. {edit_policy_propagate_admin}: {group_policy.propagateAdmin}')
            ]
        else:
            team_id = state.argument
            self.__states.clear_state(uid)
            policy_parameters = re.split(r' ', text)
            self.__backend.SetGroupPolicy(bs.TeamPolicy(
                groupId=team_id,
                allowUsersToCreateMeetings=bool(int(policy_parameters[0])),
                needApproveForMeetingCreation=bool(int(policy_parameters[1])),
                propagatePolicy=bool(int(policy_parameters[2])),
                parentVisible=bool(int(policy_parameters[3])),
                propagateAdmin=bool(int(policy_parameters[4]))))
            edit_policy_policy_updated = self.__lines.get_line('edit_policy_policy_updated', uid)
            return [
                um.ServerResponse(user_id=uid, text=f'{edit_policy_policy_updated}'),
                get_help_message(uid, self.__lines)
            ]


class AddToMeetingCmdHandler(RequestHandler):
    def handle_request(self, request) -> List[um.ServerResponse]:
        return []
        # uid = request.user_id
        # text = request.text
        # state = stateRepo.get_state(uid)
        # if request.text == '/add_to_meeting':
        #     msg = ''
        #     meetings = stub.GetOwnedMeetings(bs.EntityId(id=uid))
        #     for meeting in meetings:
        #         msg += f'/add_to_meeting{meeting.id} -- {meeting.name}\n'
        #     return [
        #         um.ServerResponse(user_id=uid, text=msg)
        #     ]
        # elif state is None:
        #     meeting_id = int(text[15:])
        #     stateRepo.set_state(uid, State('adding_to_meeting', meeting_id))
        #     add_to_meeting_tag = linesRepo.get_line('add_to_meeting_tag', uid)
        #     return [
        #         um.ServerResponse(user_id=uid, text=f'{add_to_meeting_tag}')
        #     ]
        # else:
        #     meeting_id = state.argument
        #     stateRepo.clear_state(uid)
        #     mentioned_users = map(lambda m: int(m[2:len(m) - 2]), re.findall(r'\[\[\d+\]\]', text))
        #     team_id = stub.GetMeetingInfo(bs.EntityId(id=meeting_id)).team
        #     invitable_members = map(lambda x: x.id, stub.GetInvitableMembers(bs.EntityId(id=team_id)))
        #     response = []
        #     meeting_info = stub.GetMeetingInfo(bs.EntityId(id=meeting_id))
        #     meeting_date = datetime.fromtimestamp(meeting_info.time)
        #     for mu in mentioned_users:
        #         if mu in invitable_members:
        #             stub.AddParticipant(bs.Participating(object=meeting_id, subject=mu))
        #             add_to_meeting_you_were_added = linesRepo.get_line('add_to_meeting_you_were_added', mu)
        #             response.append(um.ServerResponse(user_id=mu, text=f'{add_to_meeting_you_were_added} {meeting_info.desc}'))
        #             add_to_meeting_meeting_starts_at = linesRepo.get_line('add_to_meeting_meeting_starts_at', mu)
        #             response.append(um.ServerResponse(user_id=mu, text=f'{meeting_info.desc} {add_to_meeting_meeting_starts_at} {meeting_date}'))
        #     add_to_meeting_users_were_added = linesRepo.get_line('add_to_meeting_users_were_added', uid)
        #     response.append(um.ServerResponse(user_id=uid, text=f'{add_to_meeting_users_were_added}'))
        #     response.append(get_help_message(uid))
        #     return response


class UpdateMeetingTimeCmdHandler(RequestHandler):
    def handle_request(self, request) -> List[um.ServerResponse]:
        return []
        # uid = request.user_id
        # text = request.text
        # state = stateRepo.get_state(uid)
        # if request.text == '/update_meeting_time':
        #     msg = ''
        #     meetings = stub.GetOwnedMeetings(bs.EntityId(id=uid))
        #     for meeting in meetings:
        #         msg += f'/update_meeting_time{meeting.id} -- {meeting.name}\n'
        #     return [
        #         um.ServerResponse(user_id=uid, text=msg)
        #     ]
        # elif state is None:
        #     meeting_id = int(text[20:])
        #     stateRepo.set_state(uid, State('updating_meeting_time', meeting_id))
        #     update_meeting_time_enter_datetime = linesRepo.get_line('update_meeting_time_enter_datetime', uid)
        #     return [
        #         um.ServerResponse(user_id=uid, text=f'{update_meeting_time_enter_datetime}:')
        #     ]
        # else:
        #     meeting_id = state.argument
        #     stateRepo.clear_state(uid)
        #     dt = datetime.strptime(text, '%d-%m-%Y %H:%M')
        #     stub.UpdateMeetingInfo(bs.MeetingInfo(
        #         id=meeting_id,
        #         creator=-1,  # not important
        #         team=-1,  # not important
        #         desc='',  # not important
        #         time=int(dt.timestamp())
        #     ))
        #     response = []
        #     meeting_info = stub.GetMeetingInfo(bs.EntityId(id=meeting_id))
        #     meeting_date = datetime.fromtimestamp(meeting_info.time)
        #     update_meeting_time_time_updated = linesRepo.get_line('update_meeting_time_time_updated', uid)
        #     response.append(um.ServerResponse(user_id=uid, text=f'{meeting_info.desc} {update_meeting_time_time_updated} {meeting_date}'))
        #     response.append(get_help_message(uid))
        #     return response


class GetAgendaCmdHandler(RequestHandler):
    def handle_request(self, request) -> List[um.ServerResponse]:
        return []
        # uid = request.user_id
        # text = request.text
        # if text == '/get_agenda':
        #     get_agenda_today = linesRepo.get_line('get_agenda_today', uid)
        #     get_agenda_tomorrow = linesRepo.get_line('get_agenda_tomorrow', uid)
        #     return [
        #         um.ServerResponse(user_id=uid, text=f'/get_agenda_today -- {get_agenda_today}\n/get_agenda_tomorrow -- {get_agenda_tomorrow}')
        #     ]
        # elif text == '/get_agenda_today':
        #     start = datetime.now()
        #     start = start.replace(hour=0, minute=0, second=0, microsecond=0)
        #     end = start + timedelta(days=1)
        # else:
        #     start = datetime.now()
        #     start = start.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
        #     end = start + timedelta(days=1)
        # msg = ''
        # for info in stub.GetUserMeetings(bs.EntityId(id=uid)):
        #     meeting_info = stub.GetMeetingInfo(bs.EntityId(id=info.id))
        #     if meeting_info.time > start.timestamp() and meeting_info.time < end.timestamp():
        #         pretty_time = datetime.fromtimestamp(meeting_info.time).strftime('%H:%M')
        #         get_agenda_at = linesRepo.get_line('get_agenda_at', uid)
        #         msg += f'{meeting_info.desc} {get_agenda_at} {pretty_time}\n\n'
        # return [
        #     um.ServerResponse(user_id=uid, text=msg)
        # ]


class GCalAuthCmdHandler(RequestHandler):
    def handle_request(self, request) -> List[um.ServerResponse]:
        return []
        # uid = request.user_id
        # text = request.text
        # state = stateRepo.get_state(uid)
        # if text == '/auth_gcal':
        #     stateRepo.set_state(uid, State('authenticating_gcal', -1))
        #     url = calendar_stub.RequestAuth(cs.AuthRequest(user_id=uid)).auth_url
        #     gcal_auth_open = linesRepo.get_line('gcal_auth_open', uid)
        #     gcal_auth_respond_code = linesRepo.get_line('gcal_auth_respond_code', uid)
        #     return [
        #         um.ServerResponse(user_id=uid, text=f'{gcal_auth_open} {url}\n{gcal_auth_respond_code}')
        #     ]
        # else:
        #     stateRepo.clear_state(uid)
        #     ok = calendar_stub.FinishAuth(cs.AuthCode(user_id=uid, auth_code=text)).ok
        #     if ok:
        #         gcal_auth_authenticated = linesRepo.get_line('gcal_auth_authenticated', uid)
        #         return [
        #             um.ServerResponse(user_id=uid, text=f'{gcal_auth_authenticated}!')
        #         ]
        #     else:
        #         gcal_auth_went_wrong = linesRepo.get_line('gcal_auth_went_wrong', uid)
        #         return [
        #             um.ServerResponse(user_id=uid, text=f'{gcal_auth_went_wrong}')
        #         ]


class UploadFileCmdHandler(RequestHandler):
    def handle_request(self, request) -> List[um.ServerResponse]:
        return []
        # uid = request.user_id
        # text = request.text
        # state = stateRepo.get_state(uid)
        # if text == '/upload_file':
        #     msg = ''
        #     for info in stub.GetTeamsByUser(bs.EntityId(id=uid)):
        #         msg += f'/upload_file{info.id} -- {info.name}\n'
        #     return [
        #         um.ServerResponse(user_id=uid, text=msg)
        #     ]
        # elif state is None:
        #     group_id = int(text[12:])
        #     stateRepo.set_state(uid, State('uploading_file', group_id))
        #     upload_file_send_file = linesRepo.get_line('upload_file_send_file', uid)
        #     return [
        #         um.ServerResponse(user_id=uid, text=f'{upload_file_send_file}')
        #     ]
        # else:
        #     group_id = state.argument
        #     stateRepo.clear_state(uid)
        #     file_id = fs_stub.UploadFile(
        #         fs.FileInfo(
        #             name=request.file_name, 
        #             download_url=request.file_url
        #         )
        #     ).id
        #     stub.AddFileToTeam(bs.Participating(object=group_id, subject=file_id))
        #     upload_file_uploaded = linesRepo.get_line('upload_file_uploaded', uid)
        #     return [
        #         um.ServerResponse(user_id=uid, text=f'{upload_file_uploaded}!')
        #     ]


class GetUploadedFilesCmdHandler(RequestHandler):
    def handle_request(self, request) -> List[um.ServerResponse]:
        return []
        # uid = request.user_id
        # text = request.text
        # state = stateRepo.get_state(uid)
        # if text == '/get_files':
        #     msg = ''
        #     for info in stub.GetTeamsByUser(bs.EntityId(id=uid)):
        #         msg += f'/get_files{info.id} -- {info.name}\n'
        #     return [
        #         um.ServerResponse(user_id=uid, text=msg)
        #     ]
        # else:
        #     group_id = int(text[10:])
        #     msg = ''
        #     for item in stub.GetAvailableFiles(bs.EntityId(id=group_id)):
        #         file_info = fs_stub.DownloadFile(fs.FileId(id=item.id))
        #         msg += f'{file_info.name} -- {file_info.download_url}\n'
        #     return [
        #         um.ServerResponse(user_id=uid, text=msg)
        #     ]


class ChangeLanguageCmdHandler(RequestHandler):
    def handle_request(self, request) -> List[um.ServerResponse]:
        return []
        # uid = request.user_id
        # text = request.text
        # state = stateRepo.get_state(uid)
        # if text == '/change_language':
        #     stateRepo.set_state(uid, State('changing_language', -1))
        #     msg = ''
        #     for language in linesRepo.get_all_languages():
        #         language_name = linesRepo.get_line(language, uid)
        #         msg += f'/change_language__{language} -- {language_name}\n'
        #     return [
        #         um.ServerResponse(user_id=uid, text=msg)
        #     ]
        # elif state.action == 'changing_language':
        #     stateRepo.clear_state(uid)
        #     language = str(text[18:])
        #     linesRepo.update_user_language(uid, language)
        #     change_language_changed = linesRepo.get_line('change_language_changed', uid)
        #     msg = f'{change_language_changed}'
        #     return [
        #         um.ServerResponse(user_id=uid, text=msg),
        #         get_help_message(uid)
        #     ]


class UserMessageHandler(umg.UserMessageHandlerServicer):
    def __init__(self, backend, file_service, calendar_service):
        super().__init__()

        self.__backend = backend
        self.__file_service = file_service
        self.__calendar_service = calendar_service

        self.__state_repo = StateRepo()
        self.__lines_repo = LinesRepo()

        self.__command_handlers = CommandHandlers({
            '/start': StartCmdHandler(self.__lines_repo),
            '/help': StartCmdHandler(self.__lines_repo),
            '/create_team': CreateTeamCmdHandler(self.__state_repo, self.__backend, self.__lines_repo),
            '/invite_member': InviteUserCmdHandler(self.__state_repo, self.__backend, self.__lines_repo),
            '/accept_invite': InviteReactionCmdHandler(self.__state_repo, self.__backend, self.__lines_repo),
            '/reject_invite': InviteReactionCmdHandler(self.__state_repo, self.__backend, self.__lines_repo),
            '/create_meeting': CreateMeetingCmdHandler(self.__state_repo, self.__backend, self.__lines_repo),
            '/approve_meeting': MeetingApproveCmdHandle(self.__state_repo, self.__backend, self.__lines_repo),
            '/reject_meeting': MeetingApproveCmdHandle(self.__state_repo, self.__backend, self.__lines_repo),
            '/invite_to_meeting': InviteToMeetingCmdHandler(self.__state_repo, self.__backend, self.__lines_repo),
            '/accept_meeting_invite': MeetingInviteReactionCmdHandler(self.__state_repo, self.__backend, self.__lines_repo),
            '/reject_meeting_invite': MeetingInviteReactionCmdHandler(self.__state_repo, self.__backend, self.__lines_repo),
            '/add_child_team': AddDaughterTeamCmdHandler(self.__state_repo, self.__backend, self.__lines_repo),
            '/edit_policy': EditPolicyCmdHandler(self.__state_repo, self.__backend, self.__lines_repo),
            '/add_to_meeting': AddToMeetingCmdHandler(),
            '/update_meeting_time': UpdateMeetingTimeCmdHandler(),
            '/get_agenda': GetAgendaCmdHandler(),
            '/get_agenda_today': GetAgendaCmdHandler(),
            '/get_agenda_tomorrow': GetAgendaCmdHandler(),
            '/auth_gcal': GCalAuthCmdHandler(),
            '/upload_file': UploadFileCmdHandler(),
            '/get_files': GetUploadedFilesCmdHandler(),
            '/change_language': ChangeLanguageCmdHandler(),
            '/aom': NotificationReactionCmdHandler(self.__state_repo, self.__backend, self.__lines_repo),
            '/pom': NotificationReactionCmdHandler(self.__state_repo, self.__backend, self.__lines_repo),
            '/acc_child': AddChildTeamNotiifcationReactionCmdHandler(),
            '/rej_child': AddChildTeamNotiifcationReactionCmdHandler()
        })

        self.__states_handlers = StatesHandlers({
            'creating_team': CreateTeamCmdHandler(self.__state_repo, self.__backend, self.__lines_repo),
            'inviting_members': InviteUserCmdHandler(self.__state_repo, self.__backend, self.__lines_repo),
            'setting_meeting_desc': CreateMeetingCmdHandler(self.__state_repo, self.__backend, self.__lines_repo),
            'setting_meeting_time': CreateMeetingCmdHandler(self.__state_repo, self.__backend, self.__lines_repo),
            'inviting_to_meeting': InviteToMeetingCmdHandler(self.__state_repo, self.__backend, self.__lines_repo),
            'searching_child_team': AddDaughterTeamCmdHandler(self.__state_repo, self.__backend, self.__lines_repo),
            'adding_child_team': AddDaughterTeamCmdHandler(self.__state_repo, self.__backend, self.__lines_repo),
            'editing_policy': EditPolicyCmdHandler(self.__state_repo, self.__backend, self.__lines_repo),
            'adding_to_meeting': AddToMeetingCmdHandler(),
            'updating_meeting_time': UpdateMeetingTimeCmdHandler(),
            'authenticating_gcal': GCalAuthCmdHandler(),
            'uploading_file': UploadFileCmdHandler(),
            'changing_language': ChangeLanguageCmdHandler()
        })

    def HandleMessage(self, request, context):
        responses = self.__command_handlers.try_handle(request)
        if responses is None:
            responses = self.__states_handlers.try_handle(request, self.__state_repo.get_state(request.user_id))
        if responses is None:
            responses = [get_help_message(request.user_id)]
        for response in responses:
            yield response


def serve():
    channel = grpc.insecure_channel('nginx-service:50052')
    backend_stub = bsg.BackendServiceStub(channel)

    channel_calendar = grpc.insecure_channel('calendar-service:50053')
    calendar_stub = css.CalendarServiceStub(channel_calendar)

    
    channel_fs = grpc.insecure_channel('file-service:50054')
    fs_stub = fss.FileRepoServiceStub(channel_fs)

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    umg.add_UserMessageHandlerServicer_to_server(UserMessageHandler(backend_stub, fs_stub, calendar_stub), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    server.wait_for_termination()
