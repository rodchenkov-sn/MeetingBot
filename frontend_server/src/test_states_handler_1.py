import pytest

from states import StateRepo, State
from lines import LinesRepo

from states_handler import StatesHandlers
from frontend_server import CreateTeamCmdHandler

import user_message_pb2 as um


DEFAULT_USER_ID = 1

DEFAULT_TEAM_NAME = "team1"

CREATE_TEAM_CMD = "/create_team"

CREATING_TEAM_STATE = "creating_team"


class BackendServiceStub:
    def __init__(self):
        pass


class StatesHandlerResources:
    def __init__(self, states: StateRepo, backend: BackendServiceStub, lines: LinesRepo, handler: StatesHandlers):
        self.states = states
        self.backend = backend
        self.lines = lines
        self.handler = handler


@pytest.fixture()
def shr() -> StatesHandlerResources:
    states = StateRepo()
    backend = BackendServiceStub()
    lines = LinesRepo()
    handlers = {
        'creating_team': CreateTeamCmdHandler(states, backend, lines),
    }
    handler = StatesHandlers(handlers)
    return StatesHandlerResources(states, backend, lines, handler)


def test_try_handle_none_state(shr):
    request = um.UserMessage(
        user_id=DEFAULT_USER_ID,
        text=CREATE_TEAM_CMD
    )
    state = None
    assert shr.handler.try_handle(request, state) is None


def test_try_handle_state_action_not_in_handlers(shr):
    request = um.UserMessage(
        user_id=DEFAULT_USER_ID,
        text=CREATE_TEAM_CMD
    )
    state = State(_action="inviting_members", _argument=-1)
    assert shr.handler.try_handle(request, state) is None


def test_try_handle_state_action_in_handlers(shr):
    request = um.UserMessage(
        user_id=DEFAULT_USER_ID,
        text=DEFAULT_TEAM_NAME
    )
    state = State(_action="creating_team", _argument=-1)
    r = list(shr.handler.try_handle(request, state))
    assert shr.states.get_state(DEFAULT_USER_ID).action == CREATING_TEAM_STATE
    assert shr.states.get_state(DEFAULT_USER_ID).argument == -1
    r = r.pop()
    assert r.user_id == DEFAULT_USER_ID
    create_team_enter_name = shr.lines.get_line('create_team_enter_name', DEFAULT_USER_ID)
    assert r.text == f'{create_team_enter_name}:'
