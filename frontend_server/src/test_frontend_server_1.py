import pytest

from states import StateRepo
from lines import LinesRepo
from frontend_server import StartCmdHandler, CreateTeamCmdHandler
from frontend_server import get_help_message

import user_message_pb2 as um


DEFAULT_USER_ID = 1
DEFAULT_TEAM_NAME = "team1"
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
START_CMD_TEXT = "/start"
CREATE_TEAM_CMD_TEXT = "/create_team"


class BackendServiceStub:
    def CreateTeam(self, msg):
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
        text=START_CMD_TEXT
    )
    r = list(sch.handle_request(msg)).pop()
    assert r.user_id == DEFAULT_USER_ID
    assert r.text == HELP_MESSAGE


def test_create_team_command(fr):
    cth = CreateTeamCmdHandler(fr.states, fr.backend, fr.lines)
    msg = um.UserMessage(
        user_id=DEFAULT_USER_ID,
        text=CREATE_TEAM_CMD_TEXT
    )
    r = list(cth.handle_request(msg)).pop()
    assert r.user_id == DEFAULT_USER_ID
    assert r.text == fr.lines.get_line('create_team_enter_name', DEFAULT_USER_ID) + ":"

    msg = um.UserMessage(
        user_id=DEFAULT_USER_ID,
        text=DEFAULT_TEAM_NAME
    )
    r = list(cth.handle_request(msg))
    r1 = r.pop()
    r2 = r.pop()
    assert r1.user_id == DEFAULT_USER_ID
    assert r1.text == HELP_MESSAGE
    assert r2.user_id == DEFAULT_USER_ID
    assert r2.text == f"{DEFAULT_TEAM_NAME} {fr.lines.get_line('create_team_team_created', DEFAULT_USER_ID)}!"
