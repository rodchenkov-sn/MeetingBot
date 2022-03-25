import pytest

from states import StateRepo
from lines import LinesRepo
from frontend_server import StartCmdHandler, CreateTeamCmdHandler, InviteUserCmdHandler, InviteReactionCmdHandler
from frontend_server import get_help_message

import user_message_pb2 as um
import backend_service_pb2 as bs


DEFAULT_USER_ID = 1
DEFAULT_TEAM_ID = 1
DEFAULT_TEAM_NAME = "team1"
DEFAULT_TAGGED_USER_ID = 2

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

CREATING_TEAM_STATE = "creating_team"
INVITING_MEMBERS_STATE = "inviting_members"


class BackendServiceStub:
    def CreateTeam(self, msg):
        pass

    def GetOwnedTeams(self, msg):
        yield bs.NamedInfo(id=DEFAULT_TEAM_ID, name=DEFAULT_TEAM_NAME)

    def GetTeamInfo(self, msg):
        return bs.NamedInfo(id=DEFAULT_TEAM_ID, name=DEFAULT_TEAM_NAME)

    def GetGroupOwner(self, msg):
        return bs.EntityId(id=DEFAULT_USER_ID)

    def AddTeamMember(self, msg):
        pass

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
    assert get_help_message(DEFAULT_USER_ID, fr.lines).text == HELP_MESSAGE


def test_start_command(fr):
    sch = StartCmdHandler(fr.lines)
    msg = um.UserMessage(
        user_id=DEFAULT_USER_ID,
        text=START_CMD
    )
    r = list(sch.handle_request(msg)).pop()
    assert r.user_id == DEFAULT_USER_ID
    assert r.text == HELP_MESSAGE


def test_create_team_command(fr):
    cth = CreateTeamCmdHandler(fr.states, fr.backend, fr.lines)
    msg = um.UserMessage(
        user_id=DEFAULT_USER_ID,
        text=CREATE_TEAM_CMD
    )
    r = list(cth.handle_request(msg)).pop()
    assert fr.states.get_state(DEFAULT_USER_ID).action == CREATING_TEAM_STATE
    assert r.user_id == DEFAULT_USER_ID
    assert r.text == fr.lines.get_line('create_team_enter_name', DEFAULT_USER_ID) + ":"

    msg = um.UserMessage(
        user_id=DEFAULT_USER_ID,
        text=DEFAULT_TEAM_NAME
    )
    r = list(cth.handle_request(msg))
    assert fr.states.get_state(DEFAULT_USER_ID) is None
    r1 = r.pop()
    assert r1.user_id == DEFAULT_USER_ID
    assert r1.text == HELP_MESSAGE
    r2 = r.pop()
    assert r2.user_id == DEFAULT_USER_ID
    assert r2.text == f"{DEFAULT_TEAM_NAME} {fr.lines.get_line('create_team_team_created', DEFAULT_USER_ID)}!"


def test_invite_user_command(fr):
    iuh = InviteUserCmdHandler(fr.states, fr.backend, fr.lines)
    msg = um.UserMessage(
        user_id=DEFAULT_USER_ID,
        text=INVITE_MEMBER_CMD
    )
    r = list(iuh.handle_request(msg)).pop()
    assert r.user_id == DEFAULT_USER_ID
    assert r.text == f'{INVITE_MEMBER_CMD}{DEFAULT_TEAM_ID} -- {DEFAULT_TEAM_NAME}\n'

    msg = um.UserMessage(
        user_id=DEFAULT_USER_ID,
        text=f'{INVITE_MEMBER_CMD}{DEFAULT_TEAM_ID}'
    )
    r = list(iuh.handle_request(msg)).pop()
    assert fr.states.get_state(DEFAULT_USER_ID).action == INVITING_MEMBERS_STATE
    assert r.user_id == DEFAULT_USER_ID
    assert r.text == fr.lines.get_line('invite_user_tag_users', DEFAULT_USER_ID)

    msg = um.UserMessage(
        user_id=DEFAULT_USER_ID,
        text=f'[[{DEFAULT_TAGGED_USER_ID}]]'
    )
    r = list(iuh.handle_request(msg))
    assert fr.states.get_state(DEFAULT_USER_ID) is None
    r1 = r.pop()
    assert r1.user_id == DEFAULT_USER_ID
    assert r1.text == HELP_MESSAGE
    r2 = r.pop()
    assert r2.user_id == DEFAULT_USER_ID
    assert r2.text == fr.lines.get_line('invite_user_invitations_send', DEFAULT_USER_ID)
    r3 = r.pop()
    invite_user_you_were_invited = fr.lines.get_line('invite_user_you_were_invited', DEFAULT_TAGGED_USER_ID)
    invite_user_by = fr.lines.get_line('invite_user_by', DEFAULT_TAGGED_USER_ID)
    invite_user_accept = fr.lines.get_line('invite_user_accept', DEFAULT_TAGGED_USER_ID)
    invite_user_reject = fr.lines.get_line('invite_user_reject', DEFAULT_TAGGED_USER_ID)
    invite_msg = f'{invite_user_you_were_invited} {DEFAULT_TEAM_NAME} {invite_user_by} [[{DEFAULT_USER_ID}]]\n\n{ACCEPT_INVITE_CMD}{DEFAULT_TEAM_ID} -- {invite_user_accept}\n{REJECT_INVITE_CMD}{DEFAULT_TEAM_ID} -- {invite_user_reject}'
    assert r3.user_id == DEFAULT_TAGGED_USER_ID
    assert r3.text == invite_msg


def test_invite_reaction_command_when_accepted(fr):
    irh = InviteReactionCmdHandler(fr.states, fr.backend, fr.lines)
    msg = um.UserMessage(
        user_id=DEFAULT_TAGGED_USER_ID,
        text=f"{ACCEPT_INVITE_CMD}{DEFAULT_TEAM_ID}"
    )
    r = list(irh.handle_request(msg))
    r1 = r.pop()
    assert r1.user_id == DEFAULT_USER_ID
    invite_reaction_accepted_invitation = fr.lines.get_line('invite_reaction_accepted_invitation', DEFAULT_USER_ID)
    assert r1.text == f'[[{DEFAULT_TAGGED_USER_ID}]] {invite_reaction_accepted_invitation}'
    r2 = r.pop()
    assert r2.user_id == DEFAULT_TAGGED_USER_ID
    invite_reaction_accepted = fr.lines.get_line('invite_reaction_accepted', DEFAULT_TAGGED_USER_ID)
    assert r2.text == f"{invite_reaction_accepted}!"


def test_invite_reaction_command_when_rejected(fr):
    irh = InviteReactionCmdHandler(fr.states, fr.backend, fr.lines)
    msg = um.UserMessage(
        user_id=DEFAULT_TAGGED_USER_ID,
        text=f"{REJECT_INVITE_CMD}{DEFAULT_TEAM_ID}"
    )
    r = list(irh.handle_request(msg))
    r1 = r.pop()
    assert r1.user_id == DEFAULT_USER_ID
    invite_reaction_rejected_invitation = fr.lines.get_line('invite_reaction_rejected_invitation', DEFAULT_USER_ID)
    assert r1.text == f'[[{DEFAULT_TAGGED_USER_ID}]] {invite_reaction_rejected_invitation}'
    r2 = r.pop()
    assert r2.user_id == DEFAULT_TAGGED_USER_ID
    invite_reaction_rejected = fr.lines.get_line('invite_reaction_rejected', DEFAULT_TAGGED_USER_ID)
    assert r2.text == f'{invite_reaction_rejected}!'
