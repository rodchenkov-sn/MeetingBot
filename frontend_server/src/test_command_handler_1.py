import pytest

from states import StateRepo
from lines import LinesRepo

from command_handler import CommandHandlers
from frontend_server import CreateTeamCmdHandler

import user_message_pb2 as um


DEFAULT_USER_ID = 1

DIGITS_STRING = "12345"

UNKNOWN_CMD = "/unknown"
CREATE_TEAM_CMD = "/create_team"

CREATING_TEAM_STATE = "creating_team"


class BackendServiceStub:
    def __init__(self):
        pass


class CommandHandlersResources:
    def __init__(self, states: StateRepo, backend: BackendServiceStub, lines: LinesRepo, handler: CommandHandlers):
        self.states = states
        self.backend = backend
        self.lines = lines
        self.handler = handler


@pytest.fixture()
def cmdhndr() -> CommandHandlersResources:
    states = StateRepo()
    backend = BackendServiceStub()
    lines = LinesRepo()
    handlers = {
        '/create_team': CreateTeamCmdHandler(states, backend, lines),
    }
    handler = CommandHandlers(handlers)
    return CommandHandlersResources(states, backend, lines, handler)


def test_try_handle_none_match(cmdhndr):
    request = um.UserMessage(
        user_id=DEFAULT_USER_ID,
        text=DIGITS_STRING
    )
    assert cmdhndr.handler.try_handle(request) is None


def test_try_handle_command_not_in_handlers(cmdhndr):
    request = um.UserMessage(
        user_id=DEFAULT_USER_ID,
        text=UNKNOWN_CMD
    )
    assert cmdhndr.handler.try_handle(request) is None


def test_try_handle_command_in_handlers(cmdhndr):
    request = um.UserMessage(
        user_id=DEFAULT_USER_ID,
        text=CREATE_TEAM_CMD
    )
    r = list(cmdhndr.handler.try_handle(request))
    assert cmdhndr.states.get_state(DEFAULT_USER_ID).action == CREATING_TEAM_STATE
    assert cmdhndr.states.get_state(DEFAULT_USER_ID).argument == -1
    r = r.pop()
    assert r.user_id == DEFAULT_USER_ID
    create_team_enter_name = cmdhndr.lines.get_line('create_team_enter_name', DEFAULT_USER_ID)
    assert r.text == f'{create_team_enter_name}:'
