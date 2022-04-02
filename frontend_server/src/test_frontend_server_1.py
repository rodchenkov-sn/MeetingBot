import pytest

from datetime import datetime, timedelta

from states import StateRepo
from lines import LinesRepo

from frontend_server import StartCmdHandler, CreateTeamCmdHandler, InviteUserCmdHandler, InviteReactionCmdHandler, CreateMeetingCmdHandler, MeetingApproveCmdHandle, InviteToMeetingCmdHandler, MeetingInviteReactionCmdHandler, AddDaughterTeamCmdHandler, EditPolicyCmdHandler, NotificationReactionCmdHandler, AddChildTeamNotiifcationReactionCmdHandler
from frontend_server import get_help_message

import user_message_pb2 as um
import backend_service_pb2 as bs


DEFAULT_USER_TEAM_OWNER_ID = 1
DEFAULT_USER_TAGGED_ID = 2

DEFAULT_PARENT_TEAM_ID = 1
DEFAULT_PARENT_TEAM_NAME = "parent-team"
DEFAULT_CHILD_TEAM_ID = 2
DEFAULT_CHILD_TEAM_NAME = "child-team"

DEFAULT_MEETING_ID = 1
DEFAULT_MEETING_DESC = "meeting1"
DEFAULT_MEETING_TIME_STR = "11-11-2022 11:11"
DEFAULT_MEETING_TIME_PARSED = datetime.strptime(DEFAULT_MEETING_TIME_STR, '%d-%m-%Y %H:%M')
DEFAULT_MEETING_TIME_INT = int(DEFAULT_MEETING_TIME_PARSED.timestamp())

DEFAULT_POLICY_ALLOW_USERS_TO_CREATE_MEETINGS = True
DEFAULT_POLICY_NEED_APPROVE_FOR_MEETING_CREATION = True
DEFAULT_PROPAGATE_POLICY = True
DEFAULT_PARENT_VISIBLE = True
DEFAULT_PROPAGATE_ADMIN = True

HELP_MESSAGE = f"/create_team - to add team\n" \
    f"/invite_member - to invite user\n" \
    f"/create_meeting - to create meeting\n" \
    f"/invite_to_meeting - to invite to meeting\n" \
    f"/add_child_team - to add daughter team\n" \
    f"/edit_policy - to edit team policy\n" \
    f"/add_to_meeting - to add to meeting\n" \
    f"/update_meeting_time - to update meeting time\n" \
    f"/get_agenda - to get your agenda\n" \
    f"/upload_file - to upload file\n" \
    f"/get_files - to get available files\n" \
    f"/auth_gcal - to auth using google calendar\n" \
    f"/change_language - to change language\n" \
    f"\n/help - to see this message"

START_CMD = "/start"
CREATE_TEAM_CMD = "/create_team"
INVITE_MEMBER_CMD = "/invite_member"
ACCEPT_INVITE_CMD = "/accept_invite"
REJECT_INVITE_CMD = "/reject_invite"
CREATE_MEETING_CMD = "/create_meeting"
APPROVE_MEETING_CMD = "/approve_meeting"
REJECT_MEETING_CMD = "/reject_meeting"
INVITE_TO_MEETING_CMD = "/invite_to_meeting"
ACCEPT_MEETING_INVITE_CMD = "/accept_meeting_invite"
REJECT_MEETING_INVITE_CMD = "/reject_meeting_invite"
ADD_CHILD_TEAM_CMD = "/add_child_team"
EDIT_POLICY_CMD = "/edit_policy"
POM_CMD = "/pom"
AOM_CMD = "/aom"
ACC_CHILD_CMD = "/acc_child"
REJ_CHILD_CMD = "/rej_child"

CREATING_TEAM_STATE = "creating_team"
INVITING_MEMBERS_STATE = "inviting_members"
SETTING_MEETING_DESC_STATE = "setting_meeting_desc"
SETTING_MEETING_TIME_STATE = "setting_meeting_time"
INVITING_TO_MEETING_STATE = "inviting_to_meeting"
SEARCHING_CHILD_TEAM_STATE = "searching_child_team"
ADDING_CHILD_TEAM_STATE = "adding_child_team"
EDITING_POLICY_STATE = "editing_policy"


class BackendServiceStub:
    def CreateTeam(self, msg):
        pass

    def GetOwnedTeams(self, msg):
        yield bs.NamedInfo(id=DEFAULT_PARENT_TEAM_ID, name=DEFAULT_PARENT_TEAM_NAME)

    def GetTeamInfo(self, msg):
        return bs.NamedInfo(id=DEFAULT_PARENT_TEAM_ID, name=DEFAULT_PARENT_TEAM_NAME)

    def GetGroupOwner(self, msg):
        return bs.EntityId(id=DEFAULT_USER_TEAM_OWNER_ID)

    def AddTeamMember(self, msg):
        pass

    def GetGroupsToCreateMeeting(self, msg):
        yield bs.NamedInfo(id=DEFAULT_PARENT_TEAM_ID, name=DEFAULT_PARENT_TEAM_NAME)

    def CreateMeeting(self, msg):
        return bs.EntityId(id=DEFAULT_MEETING_ID)

    def UpdateMeetingInfo(self, msg):
        return bs.SimpleResponse(ok=True)

    def GetGroupPolicy(self, msg):
        return bs.TeamPolicy(
            groupId=DEFAULT_PARENT_TEAM_ID,
            allowUsersToCreateMeetings=DEFAULT_POLICY_ALLOW_USERS_TO_CREATE_MEETINGS,
            needApproveForMeetingCreation=DEFAULT_POLICY_NEED_APPROVE_FOR_MEETING_CREATION,
            propagatePolicy=DEFAULT_PROPAGATE_POLICY,
            parentVisible=DEFAULT_PARENT_VISIBLE,
            propagateAdmin=DEFAULT_PROPAGATE_ADMIN
        )

    def ApproveMeeting(self, msg):
        return bs.SimpleResponse(ok=True)

    def GetMeetingInfo(self, msg):
        return bs.MeetingInfo(
            id=DEFAULT_MEETING_ID,
            creator=DEFAULT_USER_TEAM_OWNER_ID,
            team=DEFAULT_PARENT_TEAM_ID,
            desc=DEFAULT_MEETING_DESC,
            time=DEFAULT_MEETING_TIME_INT
        )

    def GetOwnedMeetings(self, msg):
        yield bs.NamedInfo(id=DEFAULT_MEETING_ID, name=DEFAULT_MEETING_DESC)

    def GetInvitableMembers(self, msg):
        yield bs.EntityId(id=DEFAULT_USER_TAGGED_ID)

    def AddParticipant(self, msg):
        return bs.SimpleResponse(ok=True)

    def GetOwnedTeams(self, msg):
        return [
            bs.NamedInfo(id=DEFAULT_PARENT_TEAM_ID, name=DEFAULT_PARENT_TEAM_NAME),
            bs.NamedInfo(id=DEFAULT_CHILD_TEAM_ID, name=DEFAULT_CHILD_TEAM_NAME)
        ]

    def SetGroupPolicy(self, msg):
        return bs.SimpleResponse(ok=True)

    def AddParentTeam(self, msg):
        return bs.SimpleResponse(ok=True)


class FrontendResources:
    def __init__(self, states: StateRepo, backend: BackendServiceStub, lines: LinesRepo):
        self.states = states
        self.backend = backend
        self.lines = lines


@pytest.fixture()
def fr() -> FrontendResources:
    states = StateRepo()
    backend = BackendServiceStub()
    lines = LinesRepo()
    return FrontendResources(states, backend, lines)


def test_get_help_message(fr):
    assert get_help_message(DEFAULT_USER_TEAM_OWNER_ID, fr.lines).text == HELP_MESSAGE


def test_start_command(fr):
    sch = StartCmdHandler(fr.lines)
    msg = um.UserMessage(
        user_id=DEFAULT_USER_TEAM_OWNER_ID,
        text=START_CMD
    )
    r = list(sch.handle_request(msg))
    r = r.pop()
    assert r.user_id == DEFAULT_USER_TEAM_OWNER_ID
    assert r.text == HELP_MESSAGE


def test_create_team_command(fr):
    cth = CreateTeamCmdHandler(fr.states, fr.backend, fr.lines)
    msg = um.UserMessage(
        user_id=DEFAULT_USER_TEAM_OWNER_ID,
        text=CREATE_TEAM_CMD
    )
    r = list(cth.handle_request(msg))
    r = r.pop()
    assert fr.states.get_state(DEFAULT_USER_TEAM_OWNER_ID).action == CREATING_TEAM_STATE
    assert r.user_id == DEFAULT_USER_TEAM_OWNER_ID
    assert r.text == fr.lines.get_line('create_team_enter_name', DEFAULT_USER_TEAM_OWNER_ID) + ":"

    msg = um.UserMessage(
        user_id=DEFAULT_USER_TEAM_OWNER_ID,
        text=DEFAULT_PARENT_TEAM_NAME
    )
    r = list(cth.handle_request(msg))
    assert fr.states.get_state(DEFAULT_USER_TEAM_OWNER_ID) is None
    r1 = r.pop()
    assert r1.user_id == DEFAULT_USER_TEAM_OWNER_ID
    assert r1.text == HELP_MESSAGE
    r2 = r.pop()
    assert r2.user_id == DEFAULT_USER_TEAM_OWNER_ID
    assert r2.text == f"{DEFAULT_PARENT_TEAM_NAME} {fr.lines.get_line('create_team_team_created', DEFAULT_USER_TEAM_OWNER_ID)}!"


def test_invite_user_command(fr):
    iuh = InviteUserCmdHandler(fr.states, fr.backend, fr.lines)
    msg = um.UserMessage(
        user_id=DEFAULT_USER_TEAM_OWNER_ID,
        text=INVITE_MEMBER_CMD
    )
    rmsg = [
        f'{INVITE_MEMBER_CMD}{DEFAULT_PARENT_TEAM_ID} -- {DEFAULT_PARENT_TEAM_NAME}\n',
        f'{INVITE_MEMBER_CMD}{DEFAULT_CHILD_TEAM_ID} -- {DEFAULT_CHILD_TEAM_NAME}\n'
    ]
    r = list(iuh.handle_request(msg))
    r1 = r.pop()
    assert r1.user_id == DEFAULT_USER_TEAM_OWNER_ID
    assert r1.text in rmsg
    r2 = r.pop()
    assert r2.user_id == DEFAULT_USER_TEAM_OWNER_ID
    assert r2.text in rmsg

    msg = um.UserMessage(
        user_id=DEFAULT_USER_TEAM_OWNER_ID,
        text=f'{INVITE_MEMBER_CMD}{DEFAULT_PARENT_TEAM_ID}'
    )
    r = list(iuh.handle_request(msg))
    r = r.pop()
    assert fr.states.get_state(DEFAULT_USER_TEAM_OWNER_ID).action == INVITING_MEMBERS_STATE
    assert r.user_id == DEFAULT_USER_TEAM_OWNER_ID
    assert r.text == fr.lines.get_line('invite_user_tag_users', DEFAULT_USER_TEAM_OWNER_ID)

    msg = um.UserMessage(
        user_id=DEFAULT_USER_TEAM_OWNER_ID,
        text=f'[[{DEFAULT_USER_TAGGED_ID}]]'
    )
    r = list(iuh.handle_request(msg))
    assert fr.states.get_state(DEFAULT_USER_TEAM_OWNER_ID) is None
    r1 = r.pop()
    assert r1.user_id == DEFAULT_USER_TEAM_OWNER_ID
    assert r1.text == HELP_MESSAGE
    r2 = r.pop()
    assert r2.user_id == DEFAULT_USER_TEAM_OWNER_ID
    assert r2.text == fr.lines.get_line('invite_user_invitations_send', DEFAULT_USER_TEAM_OWNER_ID)
    r3 = r.pop()
    invite_user_you_were_invited = fr.lines.get_line('invite_user_you_were_invited', DEFAULT_USER_TAGGED_ID)
    invite_user_by = fr.lines.get_line('invite_user_by', DEFAULT_USER_TAGGED_ID)
    invite_user_accept = fr.lines.get_line('invite_user_accept', DEFAULT_USER_TAGGED_ID)
    invite_user_reject = fr.lines.get_line('invite_user_reject', DEFAULT_USER_TAGGED_ID)
    invite_msg = f'{invite_user_you_were_invited} {DEFAULT_PARENT_TEAM_NAME} {invite_user_by} [[{DEFAULT_USER_TEAM_OWNER_ID}]]\n\n{ACCEPT_INVITE_CMD}{DEFAULT_PARENT_TEAM_ID} -- {invite_user_accept}\n{REJECT_INVITE_CMD}{DEFAULT_PARENT_TEAM_ID} -- {invite_user_reject}'
    assert r3.user_id == DEFAULT_USER_TAGGED_ID
    assert r3.text == invite_msg


def test_invite_reaction_command_when_accepted(fr):
    irh = InviteReactionCmdHandler(fr.states, fr.backend, fr.lines)
    msg = um.UserMessage(
        user_id=DEFAULT_USER_TAGGED_ID,
        text=f"{ACCEPT_INVITE_CMD}{DEFAULT_PARENT_TEAM_ID}"
    )
    r = list(irh.handle_request(msg))
    r1 = r.pop()
    assert r1.user_id == DEFAULT_USER_TEAM_OWNER_ID
    invite_reaction_accepted_invitation = fr.lines.get_line('invite_reaction_accepted_invitation', DEFAULT_USER_TEAM_OWNER_ID)
    assert r1.text == f'[[{DEFAULT_USER_TAGGED_ID}]] {invite_reaction_accepted_invitation}'
    r2 = r.pop()
    assert r2.user_id == DEFAULT_USER_TAGGED_ID
    invite_reaction_accepted = fr.lines.get_line('invite_reaction_accepted', DEFAULT_USER_TAGGED_ID)
    assert r2.text == f"{invite_reaction_accepted}!"


def test_invite_reaction_command_when_rejected(fr):
    irh = InviteReactionCmdHandler(fr.states, fr.backend, fr.lines)
    msg = um.UserMessage(
        user_id=DEFAULT_USER_TAGGED_ID,
        text=f"{REJECT_INVITE_CMD}{DEFAULT_PARENT_TEAM_ID}"
    )
    r = list(irh.handle_request(msg))
    r1 = r.pop()
    assert r1.user_id == DEFAULT_USER_TEAM_OWNER_ID
    invite_reaction_rejected_invitation = fr.lines.get_line('invite_reaction_rejected_invitation', DEFAULT_USER_TEAM_OWNER_ID)
    assert r1.text == f'[[{DEFAULT_USER_TAGGED_ID}]] {invite_reaction_rejected_invitation}'
    r2 = r.pop()
    assert r2.user_id == DEFAULT_USER_TAGGED_ID
    invite_reaction_rejected = fr.lines.get_line('invite_reaction_rejected', DEFAULT_USER_TAGGED_ID)
    assert r2.text == f'{invite_reaction_rejected}!'


def test_create_meeting_command_invalid_time(fr):
    cmh = CreateMeetingCmdHandler(fr.states, fr.backend, fr.lines)
    msg = um.UserMessage(
        user_id=DEFAULT_USER_TEAM_OWNER_ID,
        text=CREATE_MEETING_CMD
    )
    r = list(cmh.handle_request(msg))
    r = r.pop()
    assert r.user_id == DEFAULT_USER_TEAM_OWNER_ID
    assert r.text == f'{CREATE_MEETING_CMD}{DEFAULT_PARENT_TEAM_ID} -- {DEFAULT_PARENT_TEAM_NAME}\n'

    msg = um.UserMessage(
        user_id=DEFAULT_USER_TEAM_OWNER_ID,
        text=f"{CREATE_MEETING_CMD}{DEFAULT_PARENT_TEAM_ID}"
    )
    r = list(cmh.handle_request(msg))
    r = r.pop()
    assert fr.states.get_state(DEFAULT_USER_TEAM_OWNER_ID).action == SETTING_MEETING_DESC_STATE
    assert fr.states.get_state(DEFAULT_USER_TEAM_OWNER_ID).argument == DEFAULT_MEETING_ID
    assert fr.states.get_state(DEFAULT_USER_TEAM_OWNER_ID).argument2 == DEFAULT_PARENT_TEAM_ID
    assert r.user_id == DEFAULT_USER_TEAM_OWNER_ID
    create_meeting_enter_description = fr.lines.get_line('create_meeting_enter_description', DEFAULT_USER_TEAM_OWNER_ID)
    assert r.text == f'{create_meeting_enter_description}:'

    msg = um.UserMessage(
        user_id=DEFAULT_USER_TEAM_OWNER_ID,
        text=DEFAULT_MEETING_DESC
    )
    r = list(cmh.handle_request(msg))
    r = r.pop()
    assert fr.states.get_state(DEFAULT_USER_TEAM_OWNER_ID).action == SETTING_MEETING_TIME_STATE
    assert fr.states.get_state(DEFAULT_USER_TEAM_OWNER_ID).argument == DEFAULT_MEETING_ID
    assert fr.states.get_state(DEFAULT_USER_TEAM_OWNER_ID).argument2 == DEFAULT_PARENT_TEAM_ID
    assert r.user_id == DEFAULT_USER_TEAM_OWNER_ID
    create_meeting_enter_datetime = fr.lines.get_line('create_meeting_enter_datetime', DEFAULT_USER_TEAM_OWNER_ID)
    assert r.text == f'{create_meeting_enter_datetime}:'

    msg = um.UserMessage(
        user_id=DEFAULT_USER_TEAM_OWNER_ID,
        text="123 456"
    )
    r = list(cmh.handle_request(msg))
    r = r.pop()
    assert r.user_id == DEFAULT_USER_TEAM_OWNER_ID
    assert r.text == f'try again!'


def test_create_meeting_command_valid_time_team_owner(fr):
    cmh = CreateMeetingCmdHandler(fr.states, fr.backend, fr.lines)
    msg = um.UserMessage(
        user_id=DEFAULT_USER_TEAM_OWNER_ID,
        text=CREATE_MEETING_CMD
    )
    r = list(cmh.handle_request(msg))
    r = r.pop()
    assert r.user_id == DEFAULT_USER_TEAM_OWNER_ID
    assert r.text == f'{CREATE_MEETING_CMD}{DEFAULT_PARENT_TEAM_ID} -- {DEFAULT_PARENT_TEAM_NAME}\n'

    msg = um.UserMessage(
        user_id=DEFAULT_USER_TEAM_OWNER_ID,
        text=f"{CREATE_MEETING_CMD}{DEFAULT_PARENT_TEAM_ID}"
    )
    r = list(cmh.handle_request(msg))
    r = r.pop()
    assert fr.states.get_state(DEFAULT_USER_TEAM_OWNER_ID).action == SETTING_MEETING_DESC_STATE
    assert fr.states.get_state(DEFAULT_USER_TEAM_OWNER_ID).argument == DEFAULT_MEETING_ID
    assert fr.states.get_state(DEFAULT_USER_TEAM_OWNER_ID).argument2 == DEFAULT_PARENT_TEAM_ID
    assert r.user_id == DEFAULT_USER_TEAM_OWNER_ID
    create_meeting_enter_description = fr.lines.get_line('create_meeting_enter_description', DEFAULT_USER_TEAM_OWNER_ID)
    assert r.text == f'{create_meeting_enter_description}:'

    msg = um.UserMessage(
        user_id=DEFAULT_USER_TEAM_OWNER_ID,
        text=DEFAULT_MEETING_DESC
    )
    r = list(cmh.handle_request(msg))
    r = r.pop()
    assert fr.states.get_state(DEFAULT_USER_TEAM_OWNER_ID).action == SETTING_MEETING_TIME_STATE
    assert fr.states.get_state(DEFAULT_USER_TEAM_OWNER_ID).argument == DEFAULT_MEETING_ID
    assert fr.states.get_state(DEFAULT_USER_TEAM_OWNER_ID).argument2 == DEFAULT_PARENT_TEAM_ID
    assert r.user_id == DEFAULT_USER_TEAM_OWNER_ID
    create_meeting_enter_datetime = fr.lines.get_line('create_meeting_enter_datetime', DEFAULT_USER_TEAM_OWNER_ID)
    assert r.text == f'{create_meeting_enter_datetime}:'

    msg = um.UserMessage(
        user_id=DEFAULT_USER_TEAM_OWNER_ID,
        text=DEFAULT_MEETING_TIME_STR
    )
    r = list(cmh.handle_request(msg))
    assert fr.states.get_state(DEFAULT_USER_TEAM_OWNER_ID) is None
    r1 = r.pop()
    assert r1.user_id == DEFAULT_USER_TEAM_OWNER_ID
    assert r1.text == f'{DEFAULT_MEETING_DESC} in T - 5!'
    assert r1.timestamp == int((DEFAULT_MEETING_TIME_PARSED - timedelta(minutes=5)).timestamp())
    r2 = r.pop()
    assert r2.user_id == DEFAULT_USER_TEAM_OWNER_ID
    create_meeting_meeting_created = fr.lines.get_line('create_meeting_meeting_created', DEFAULT_USER_TEAM_OWNER_ID)
    assert r2.text == f'{create_meeting_meeting_created}!'


def test_create_meeting_command_valid_time_need_approve(fr):
    cmh = CreateMeetingCmdHandler(fr.states, fr.backend, fr.lines)
    msg = um.UserMessage(
        user_id=DEFAULT_USER_TAGGED_ID,
        text=CREATE_MEETING_CMD
    )
    r = list(cmh.handle_request(msg))
    r = r.pop()
    assert r.user_id == DEFAULT_USER_TAGGED_ID
    assert r.text == f'{CREATE_MEETING_CMD}{DEFAULT_PARENT_TEAM_ID} -- {DEFAULT_PARENT_TEAM_NAME}\n'

    msg = um.UserMessage(
        user_id=DEFAULT_USER_TAGGED_ID,
        text=f"{CREATE_MEETING_CMD}{DEFAULT_PARENT_TEAM_ID}"
    )
    r = list(cmh.handle_request(msg))
    r = r.pop()
    assert fr.states.get_state(DEFAULT_USER_TAGGED_ID).action == SETTING_MEETING_DESC_STATE
    assert fr.states.get_state(DEFAULT_USER_TAGGED_ID).argument == DEFAULT_MEETING_ID
    assert fr.states.get_state(DEFAULT_USER_TAGGED_ID).argument2 == DEFAULT_PARENT_TEAM_ID
    assert r.user_id == DEFAULT_USER_TAGGED_ID
    create_meeting_enter_description = fr.lines.get_line('create_meeting_enter_description', DEFAULT_USER_TAGGED_ID)
    assert r.text == f'{create_meeting_enter_description}:'

    msg = um.UserMessage(
        user_id=DEFAULT_USER_TAGGED_ID,
        text=DEFAULT_MEETING_DESC
    )
    r = list(cmh.handle_request(msg))
    r = r.pop()
    assert fr.states.get_state(DEFAULT_USER_TAGGED_ID).action == SETTING_MEETING_TIME_STATE
    assert fr.states.get_state(DEFAULT_USER_TAGGED_ID).argument == DEFAULT_MEETING_ID
    assert fr.states.get_state(DEFAULT_USER_TAGGED_ID).argument2 == DEFAULT_PARENT_TEAM_ID
    assert r.user_id == DEFAULT_USER_TAGGED_ID
    create_meeting_enter_datetime = fr.lines.get_line('create_meeting_enter_datetime', DEFAULT_USER_TAGGED_ID)
    assert r.text == f'{create_meeting_enter_datetime}:'

    msg = um.UserMessage(
        user_id=DEFAULT_USER_TAGGED_ID,
        text=DEFAULT_MEETING_TIME_STR
    )
    r = list(cmh.handle_request(msg))
    assert fr.states.get_state(DEFAULT_USER_TAGGED_ID) is None
    r1 = r.pop()
    assert r1.user_id == DEFAULT_USER_TEAM_OWNER_ID
    create_meeting_user = fr.lines.get_line('create_meeting_user', DEFAULT_USER_TEAM_OWNER_ID)
    create_meeting_created_meeting = fr.lines.get_line('create_meeting_created_meeting', DEFAULT_USER_TEAM_OWNER_ID)
    create_meeting_approve = fr.lines.get_line('create_meeting_approve', DEFAULT_USER_TEAM_OWNER_ID)
    create_meeting_reject = fr.lines.get_line('create_meeting_reject', DEFAULT_USER_TEAM_OWNER_ID)
    assert r1.text == f'{create_meeting_user} [[{DEFAULT_USER_TAGGED_ID}]] {create_meeting_created_meeting} {DEFAULT_MEETING_DESC}\n{APPROVE_MEETING_CMD}{DEFAULT_MEETING_ID} -- {create_meeting_approve}\n{REJECT_MEETING_CMD}{DEFAULT_MEETING_ID} -- {create_meeting_reject}'
    r2 = r.pop()
    assert r2.user_id == DEFAULT_USER_TAGGED_ID
    create_meeting_wait_approval = fr.lines.get_line('create_meeting_wait_approval', DEFAULT_USER_TAGGED_ID)
    assert r2.text == f'{create_meeting_wait_approval}'


def test_meeting_approve_command_approve(fr):
    mah = MeetingApproveCmdHandle(fr.states, fr.backend, fr.lines)
    msg = um.UserMessage(
        user_id=DEFAULT_USER_TEAM_OWNER_ID,
        text=f"{APPROVE_MEETING_CMD}{DEFAULT_MEETING_ID}"
    )
    r = list(mah.handle_request(msg))
    r1 = r.pop()
    assert r1.user_id == DEFAULT_USER_TEAM_OWNER_ID # DEFAULT_USER_TAGGED_ID
    meeting_approve_meeting = fr.lines.get_line('meeting_approve_meeting', DEFAULT_USER_TAGGED_ID)
    meeting_approve_was_approved = fr.lines.get_line('meeting_approve_was_approved', DEFAULT_USER_TAGGED_ID)
    assert r1.text == f'{meeting_approve_meeting} {DEFAULT_MEETING_DESC} {meeting_approve_was_approved}'
    r2 = r.pop()
    assert r2.user_id == DEFAULT_USER_TEAM_OWNER_ID
    meeting_approve_approved = fr.lines.get_line('meeting_approve_approved', DEFAULT_USER_TEAM_OWNER_ID)
    assert r2.text == f'{meeting_approve_approved}!'


def test_meeting_approve_command_reject(fr):
    mah = MeetingApproveCmdHandle(fr.states, fr.backend, fr.lines)
    msg = um.UserMessage(
        user_id=DEFAULT_USER_TEAM_OWNER_ID,
        text=f"{REJECT_MEETING_CMD}{DEFAULT_MEETING_ID}"
    )
    r = list(mah.handle_request(msg))
    r1 = r.pop()
    assert r1.user_id == DEFAULT_USER_TEAM_OWNER_ID  # DEFAULT_USER_TAGGED_ID
    meeting_approve_meeting = fr.lines.get_line('meeting_approve_meeting', DEFAULT_USER_TAGGED_ID)
    meeting_approve_was_rejected = fr.lines.get_line('meeting_approve_was_rejected', DEFAULT_USER_TAGGED_ID)
    assert r1.text == f'{meeting_approve_meeting} {DEFAULT_MEETING_DESC} {meeting_approve_was_rejected}'
    r2 = r.pop()
    assert r2.user_id == DEFAULT_USER_TEAM_OWNER_ID
    meeting_approve_rejected = fr.lines.get_line('meeting_approve_rejected', DEFAULT_USER_TEAM_OWNER_ID)
    assert r2.text == f'{meeting_approve_rejected}!'


def test_invite_to_meeting_command(fr):
    itmh = InviteToMeetingCmdHandler(fr.states, fr.backend, fr.lines)
    msg = um.UserMessage(
        user_id=DEFAULT_USER_TEAM_OWNER_ID,
        text=INVITE_TO_MEETING_CMD
    )
    r = list(itmh.handle_request(msg))
    r = r.pop()
    assert r.user_id == DEFAULT_USER_TEAM_OWNER_ID
    assert r.text == f'{INVITE_TO_MEETING_CMD}{DEFAULT_MEETING_ID} -- {DEFAULT_MEETING_DESC}\n'

    msg = um.UserMessage(
        user_id=DEFAULT_USER_TEAM_OWNER_ID,
        text=f'{INVITE_TO_MEETING_CMD}{DEFAULT_MEETING_ID}'
    )
    r = list(itmh.handle_request(msg))
    r = r.pop()
    assert fr.states.get_state(DEFAULT_USER_TEAM_OWNER_ID).action == INVITING_TO_MEETING_STATE
    assert fr.states.get_state(DEFAULT_USER_TEAM_OWNER_ID).argument == DEFAULT_MEETING_ID
    assert r.user_id == DEFAULT_USER_TEAM_OWNER_ID
    inviting_to_meeting_tag = fr.lines.get_line('inviting_to_meeting_tag', DEFAULT_USER_TEAM_OWNER_ID)
    assert r.text == f'{inviting_to_meeting_tag}'

    msg = um.UserMessage(
        user_id=DEFAULT_USER_TEAM_OWNER_ID,
        text=f"[[{DEFAULT_USER_TAGGED_ID}]]"
    )
    r = list(itmh.handle_request(msg))
    assert fr.states.get_state(DEFAULT_USER_TEAM_OWNER_ID) is None
    r1 = r.pop()
    assert r1.user_id == DEFAULT_USER_TEAM_OWNER_ID
    assert r1.text == HELP_MESSAGE
    r2 = r.pop()
    assert r2.user_id == DEFAULT_USER_TEAM_OWNER_ID
    inviting_to_meeting_invitations_send = fr.lines.get_line('inviting_to_meeting_invitations_send', DEFAULT_USER_TEAM_OWNER_ID)
    assert r2.text == f'{inviting_to_meeting_invitations_send}'
    r3 = r.pop()
    assert r3.user_id == DEFAULT_USER_TAGGED_ID
    inviting_to_meeting_you_were_invited = fr.lines.get_line('inviting_to_meeting_you_were_invited', DEFAULT_USER_TAGGED_ID)
    inviting_to_meeting_by = fr.lines.get_line('inviting_to_meeting_by', DEFAULT_USER_TAGGED_ID)
    inviting_to_meeting_accept = fr.lines.get_line('inviting_to_meeting_accept', DEFAULT_USER_TAGGED_ID)
    inviting_to_meeting_reject = fr.lines.get_line('inviting_to_meeting_reject', DEFAULT_USER_TAGGED_ID)
    invite_msg = f'{inviting_to_meeting_you_were_invited} {DEFAULT_MEETING_DESC} {inviting_to_meeting_by} [[{DEFAULT_USER_TEAM_OWNER_ID}]]\n\n{ACCEPT_MEETING_INVITE_CMD}{DEFAULT_MEETING_ID} -- {inviting_to_meeting_accept}\n{REJECT_MEETING_INVITE_CMD}{DEFAULT_MEETING_ID} -- {inviting_to_meeting_reject}'
    assert r3.text == invite_msg


def test_meeting_invite_reaction_accept(fr):
    mirh = MeetingInviteReactionCmdHandler(fr.states, fr.backend, fr.lines)
    msg = um.UserMessage(
        user_id=DEFAULT_USER_TAGGED_ID,
        text=f"{ACCEPT_MEETING_INVITE_CMD}{DEFAULT_MEETING_ID}"
    )
    r = list(mirh.handle_request(msg))
    r1 = r.pop()
    assert r1.user_id == DEFAULT_USER_TEAM_OWNER_ID
    meeting_invite_reaction_accepted = fr.lines.get_line('meeting_invite_reaction_accepted', DEFAULT_USER_TEAM_OWNER_ID)
    assert r1.text == f'[[{DEFAULT_USER_TAGGED_ID}]] {meeting_invite_reaction_accepted}'
    r2 = r.pop()
    assert r2.user_id == DEFAULT_USER_TAGGED_ID
    meeting_date = datetime.fromtimestamp(DEFAULT_MEETING_TIME_INT)
    meeting_invite_reaction_meeting_starts_at = fr.lines.get_line('meeting_invite_reaction_meeting_starts_at', DEFAULT_USER_TAGGED_ID)
    assert r2.text == f'{DEFAULT_MEETING_DESC} {meeting_invite_reaction_meeting_starts_at} {meeting_date}'
    r3 = r.pop()
    assert r3.user_id == DEFAULT_USER_TAGGED_ID
    meeting_invite_reaction_you_accepted = fr.lines.get_line('meeting_invite_reaction_you_accepted', DEFAULT_USER_TAGGED_ID)
    assert r3.text == f'{meeting_invite_reaction_you_accepted}'
    r4 = r.pop()
    assert r4.user_id == DEFAULT_USER_TAGGED_ID
    assert r4.text == f'{DEFAULT_MEETING_DESC} in T - 5!\n\n{POM_CMD}{DEFAULT_MEETING_ID} -- heading!\n{AOM_CMD}{DEFAULT_MEETING_ID} -- ignore'


def test_meeting_invite_reaction_reject(fr):
    mirh = MeetingInviteReactionCmdHandler(fr.states, fr.backend, fr.lines)
    msg = um.UserMessage(
        user_id=DEFAULT_USER_TAGGED_ID,
        text=f"{REJECT_MEETING_INVITE_CMD}{DEFAULT_MEETING_ID}"
    )
    r = list(mirh.handle_request(msg))
    r1 = r.pop()
    assert r1.user_id == DEFAULT_USER_TEAM_OWNER_ID
    meeting_invite_reaction_rejected = fr.lines.get_line('meeting_invite_reaction_rejected', DEFAULT_USER_TEAM_OWNER_ID)
    assert r1.text == f'[[{DEFAULT_USER_TAGGED_ID}]] {meeting_invite_reaction_rejected}'
    r2 = r.pop()
    assert r2.user_id == DEFAULT_USER_TAGGED_ID
    meeting_invite_reaction_you_rejected = fr.lines.get_line('meeting_invite_reaction_you_rejected', DEFAULT_USER_TAGGED_ID)
    assert r2.text == f'{meeting_invite_reaction_you_rejected}'


def test_add_daughter_team_command_mention_many(fr):
    adth = AddDaughterTeamCmdHandler(fr.states, fr.backend, fr.lines)
    msg = um.UserMessage(
        user_id=DEFAULT_USER_TEAM_OWNER_ID,
        text=ADD_CHILD_TEAM_CMD
    )
    add_daughter_team_add_to = fr.lines.get_line('add_daughter_team_add_to', DEFAULT_USER_TEAM_OWNER_ID)
    rmsg = [
        f'{ADD_CHILD_TEAM_CMD}{DEFAULT_PARENT_TEAM_ID} -- {add_daughter_team_add_to} {DEFAULT_PARENT_TEAM_NAME}\n',
        f'{ADD_CHILD_TEAM_CMD}{DEFAULT_CHILD_TEAM_ID} -- {add_daughter_team_add_to} {DEFAULT_CHILD_TEAM_NAME}\n'
    ]
    r = list(adth.handle_request(msg))
    r1 = r.pop()
    assert r1.user_id == DEFAULT_USER_TEAM_OWNER_ID
    assert r1.text in rmsg
    r2 = r.pop()
    assert r2.user_id == DEFAULT_USER_TEAM_OWNER_ID
    assert r2.text in rmsg

    msg = um.UserMessage(
        user_id=DEFAULT_USER_TEAM_OWNER_ID,
        text=f'{ADD_CHILD_TEAM_CMD}{DEFAULT_PARENT_TEAM_ID}'
    )
    r = list(adth.handle_request(msg))
    assert fr.states.get_state(DEFAULT_USER_TEAM_OWNER_ID).action == SEARCHING_CHILD_TEAM_STATE
    assert fr.states.get_state(DEFAULT_USER_TEAM_OWNER_ID).argument == DEFAULT_PARENT_TEAM_ID
    r = r.pop()
    assert r.user_id == DEFAULT_USER_TEAM_OWNER_ID
    assert r.text == f'mention team owner:'

    msg = um.UserMessage(
        user_id=DEFAULT_USER_TEAM_OWNER_ID,
        text=f'[[{DEFAULT_USER_TEAM_OWNER_ID}]][[{DEFAULT_USER_TAGGED_ID}]]'
    )
    r = list(adth.handle_request(msg))
    r = r.pop()
    assert r.user_id == DEFAULT_USER_TEAM_OWNER_ID
    assert r.text == 'mention only one user pls'


def test_add_daughter_team_command_mention_one(fr):
    adth = AddDaughterTeamCmdHandler(fr.states, fr.backend, fr.lines)
    msg = um.UserMessage(
        user_id=DEFAULT_USER_TEAM_OWNER_ID,
        text=ADD_CHILD_TEAM_CMD
    )
    add_daughter_team_add_to = fr.lines.get_line('add_daughter_team_add_to', DEFAULT_USER_TEAM_OWNER_ID)
    rmsg = [
        f'{ADD_CHILD_TEAM_CMD}{DEFAULT_PARENT_TEAM_ID} -- {add_daughter_team_add_to} {DEFAULT_PARENT_TEAM_NAME}\n',
        f'{ADD_CHILD_TEAM_CMD}{DEFAULT_CHILD_TEAM_ID} -- {add_daughter_team_add_to} {DEFAULT_CHILD_TEAM_NAME}\n'
    ]
    r = list(adth.handle_request(msg))
    r1 = r.pop()
    assert r1.user_id == DEFAULT_USER_TEAM_OWNER_ID
    assert r1.text in rmsg
    r2 = r.pop()
    assert r2.user_id == DEFAULT_USER_TEAM_OWNER_ID
    assert r2.text in rmsg

    msg = um.UserMessage(
        user_id=DEFAULT_USER_TEAM_OWNER_ID,
        text=f'{ADD_CHILD_TEAM_CMD}{DEFAULT_PARENT_TEAM_ID}'
    )
    r = list(adth.handle_request(msg))
    assert fr.states.get_state(DEFAULT_USER_TEAM_OWNER_ID).action == SEARCHING_CHILD_TEAM_STATE
    assert fr.states.get_state(DEFAULT_USER_TEAM_OWNER_ID).argument == DEFAULT_PARENT_TEAM_ID
    r = r.pop()
    assert r.user_id == DEFAULT_USER_TEAM_OWNER_ID
    assert r.text == f'mention team owner:'

    msg = um.UserMessage(
        user_id=DEFAULT_USER_TEAM_OWNER_ID,
        text=f'[[{DEFAULT_USER_TEAM_OWNER_ID}]]'
    )
    rmsg = [
        f'{ADD_CHILD_TEAM_CMD}{DEFAULT_PARENT_TEAM_ID} -- {DEFAULT_PARENT_TEAM_NAME}\n',
        f'{ADD_CHILD_TEAM_CMD}{DEFAULT_CHILD_TEAM_ID} -- {DEFAULT_CHILD_TEAM_NAME}\n'
    ]
    r = list(adth.handle_request(msg))
    r1 = r.pop()
    assert r1.user_id == DEFAULT_USER_TEAM_OWNER_ID
    assert r1.text in rmsg
    r2 = r.pop()
    assert r2.user_id == DEFAULT_USER_TEAM_OWNER_ID
    assert r2.text in rmsg
    assert fr.states.get_state(DEFAULT_USER_TEAM_OWNER_ID).action == ADDING_CHILD_TEAM_STATE
    assert fr.states.get_state(DEFAULT_USER_TEAM_OWNER_ID).argument == DEFAULT_PARENT_TEAM_ID
    assert fr.states.get_state(DEFAULT_USER_TEAM_OWNER_ID).argument2 == DEFAULT_USER_TEAM_OWNER_ID

    msg = um.UserMessage(
        user_id=DEFAULT_USER_TEAM_OWNER_ID,
        text=f'{ADD_CHILD_TEAM_CMD}{DEFAULT_PARENT_TEAM_ID}'  # DEFAULT_CHILD_TEAM_ID
    )
    r = list(adth.handle_request(msg))
    assert fr.states.get_state(DEFAULT_USER_TEAM_OWNER_ID) is None
    r1 = r.pop()
    assert r1.user_id == DEFAULT_USER_TEAM_OWNER_ID  # DEFAULT_CHILD_TEAM_ID
    assert r1.text == f'[[{DEFAULT_USER_TEAM_OWNER_ID}]] wants to add {DEFAULT_PARENT_TEAM_NAME} to {DEFAULT_PARENT_TEAM_NAME} children\n\n{ACC_CHILD_CMD}{DEFAULT_PARENT_TEAM_ID}_{DEFAULT_PARENT_TEAM_ID} -- accept\n{REJ_CHILD_CMD}{DEFAULT_PARENT_TEAM_ID}_{DEFAULT_PARENT_TEAM_ID} -- reject'  # DEFAULT_CHILD_TEAM_ID DEFAULT_CHILD_TEAM_NAME
    r2 = r.pop()
    assert r2.user_id == DEFAULT_USER_TEAM_OWNER_ID
    assert r2.text == HELP_MESSAGE
    r3 = r.pop()
    assert r3.user_id == DEFAULT_USER_TEAM_OWNER_ID
    assert r3.text == 'invitation was sent'


def test_edit_policy_command(fr):
    eph = EditPolicyCmdHandler(fr.states, fr.backend, fr.lines)
    msg = um.UserMessage(
        user_id=DEFAULT_USER_TEAM_OWNER_ID,
        text=f'{EDIT_POLICY_CMD}'
    )
    edit_policy_edit_of = fr.lines.get_line('edit_policy_edit_of', DEFAULT_USER_TEAM_OWNER_ID)
    rmsg = [
        f'{EDIT_POLICY_CMD}{DEFAULT_PARENT_TEAM_ID} -- {edit_policy_edit_of} {DEFAULT_PARENT_TEAM_NAME}\n',
        f'{EDIT_POLICY_CMD}{DEFAULT_CHILD_TEAM_ID} -- {edit_policy_edit_of} {DEFAULT_CHILD_TEAM_NAME}\n'
    ]
    r = list(eph.handle_request(msg))
    r1 = r.pop()
    assert r1.user_id == DEFAULT_USER_TEAM_OWNER_ID
    assert r1.text in rmsg
    r2 = r.pop()
    assert r2.user_id == DEFAULT_USER_TEAM_OWNER_ID
    assert r2.text in rmsg

    msg = um.UserMessage(
        user_id=DEFAULT_USER_TEAM_OWNER_ID,
        text=f'{EDIT_POLICY_CMD}{DEFAULT_PARENT_TEAM_ID}'
    )
    r = list(eph.handle_request(msg))
    assert fr.states.get_state(DEFAULT_USER_TEAM_OWNER_ID).action == EDITING_POLICY_STATE
    assert fr.states.get_state(DEFAULT_USER_TEAM_OWNER_ID).argument == DEFAULT_PARENT_TEAM_ID
    r1 = r.pop()
    assert r1.user_id == DEFAULT_USER_TEAM_OWNER_ID
    edit_policy_propagate_admin = fr.lines.get_line('edit_policy_propagate_admin', DEFAULT_USER_TEAM_OWNER_ID)
    assert r1.text == f'\n5. {edit_policy_propagate_admin}: {True}'
    r2 = r.pop()
    assert r2.user_id == DEFAULT_USER_TEAM_OWNER_ID
    edit_policy_parent_visible = fr.lines.get_line('edit_policy_parent_visible', DEFAULT_USER_TEAM_OWNER_ID)
    assert r2.text == f'\n4. {edit_policy_parent_visible}: {True}'
    r3 = r.pop()
    assert r3.user_id == DEFAULT_USER_TEAM_OWNER_ID
    edit_policy_propagate_policy = fr.lines.get_line('edit_policy_propagate_policy', DEFAULT_USER_TEAM_OWNER_ID)
    assert r3.text == f'\n3. {edit_policy_propagate_policy}: {True}'
    r4 = r.pop()
    assert r4.user_id == DEFAULT_USER_TEAM_OWNER_ID
    edit_policy_need_approve = fr.lines.get_line('edit_policy_need_approve', DEFAULT_USER_TEAM_OWNER_ID)
    assert r4.text == f'\n2. {edit_policy_need_approve}: {True}'
    r5 = r.pop()
    assert r5.user_id == DEFAULT_USER_TEAM_OWNER_ID
    edit_policy_allow_meetings = fr.lines.get_line('edit_policy_allow_meetings', DEFAULT_USER_TEAM_OWNER_ID)
    assert r5.text == f'\n1. {edit_policy_allow_meetings}: {True}'
    r6 = r.pop()
    assert r6.user_id == DEFAULT_USER_TEAM_OWNER_ID
    edit_policy_enter_one_zero = fr.lines.get_line('edit_policy_enter_one_zero', DEFAULT_USER_TEAM_OWNER_ID)
    assert r6.text == f'{edit_policy_enter_one_zero}:'

    msg = um.UserMessage(
        user_id=DEFAULT_USER_TEAM_OWNER_ID,
        text="0 0 0 0 0"
    )
    r = list(eph.handle_request(msg))
    assert fr.states.get_state(DEFAULT_USER_TEAM_OWNER_ID) is None
    r1 = r.pop()
    assert r1.user_id == DEFAULT_USER_TEAM_OWNER_ID
    assert r1.text == HELP_MESSAGE
    r2 = r.pop()
    assert r2.user_id == DEFAULT_USER_TEAM_OWNER_ID
    edit_policy_policy_updated = fr.lines.get_line('edit_policy_policy_updated', DEFAULT_USER_TEAM_OWNER_ID)
    assert r2.text == f'{edit_policy_policy_updated}'


def test_notification_reaction_command_pom(fr):
    nrh = NotificationReactionCmdHandler(fr.states, fr.backend, fr.lines)
    msg = um.UserMessage(
        user_id=DEFAULT_USER_TAGGED_ID,
        text=f'{POM_CMD}{DEFAULT_MEETING_ID}'
    )
    r = list(nrh.handle_request(msg))
    r1 = r.pop()
    assert r1.user_id == DEFAULT_USER_TEAM_OWNER_ID
    assert r1.text == f'[[{DEFAULT_USER_TAGGED_ID}]] id heading to {DEFAULT_MEETING_DESC}'
    r2 = r.pop()
    assert r2.user_id == DEFAULT_USER_TAGGED_ID
    assert r2.text == 'Understandable have a nice day'


def test_notification_reaction_command_aom(fr):
    nrh = NotificationReactionCmdHandler(fr.states, fr.backend, fr.lines)
    msg = um.UserMessage(
        user_id=DEFAULT_USER_TAGGED_ID,
        text=f'{AOM_CMD}{DEFAULT_MEETING_ID}'
    )
    r = list(nrh.handle_request(msg))
    r1 = r.pop()
    assert r1.user_id == DEFAULT_USER_TEAM_OWNER_ID
    assert r1.text == f'[[{DEFAULT_USER_TAGGED_ID}]] wont be at {DEFAULT_MEETING_DESC}'
    r2 = r.pop()
    assert r2.user_id == DEFAULT_USER_TAGGED_ID
    assert r2.text == 'Understandable have a nice day'


def test_add_child_team_notification_reaction_accept(fr):
    actnr = AddChildTeamNotiifcationReactionCmdHandler(fr.states, fr.backend, fr.lines)
    msg = um.UserMessage(
        user_id=DEFAULT_USER_TEAM_OWNER_ID,
        text=f'{ACC_CHILD_CMD}{DEFAULT_PARENT_TEAM_ID}_{DEFAULT_PARENT_TEAM_ID}'
    )
    r = list(actnr.handle_request(msg))
    r1 = r.pop()
    assert r1.user_id == DEFAULT_USER_TEAM_OWNER_ID
    assert r1.text == f'[[{DEFAULT_USER_TEAM_OWNER_ID}]] team is now your child'
    r2 = r.pop()
    assert r2.user_id == DEFAULT_USER_TEAM_OWNER_ID
    assert r2.text == 'understandable'


def test_add_child_team_notification_reaction_reject(fr):
    actnr = AddChildTeamNotiifcationReactionCmdHandler(fr.states, fr.backend, fr.lines)
    msg = um.UserMessage(
        user_id=DEFAULT_USER_TEAM_OWNER_ID,
        text=f'{REJ_CHILD_CMD}{DEFAULT_PARENT_TEAM_ID}_{DEFAULT_PARENT_TEAM_ID}'
    )
    r = list(actnr.handle_request(msg))
    r1 = r.pop()
    assert r1.user_id == DEFAULT_USER_TEAM_OWNER_ID
    assert r1.text == f'[[{DEFAULT_USER_TEAM_OWNER_ID}]] rejected child invitation'
    r2 = r.pop()
    assert r2.user_id == DEFAULT_USER_TEAM_OWNER_ID
    assert r2.text == 'understandable'
