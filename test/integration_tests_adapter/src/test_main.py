import pytest
import grpc
import re

import user_message_pb2_grpc as ums
import user_message_pb2 as um

channel = grpc.insecure_channel('frontend-service:50051')
stub = ums.UserMessageHandlerStub(channel)

# user id
DEFAULT_USER_ID_HELP = 1
DEFAULT_USER_ID_CREATE_TEAM = 2
DEFAULT_USER_ID_INVITE_USER = 3
DEFAULT_TAGGED_USER_ID_INVITE_USER = 4
# team name
DEFAULT_TEAM_NAME_CREATE_TEAM = 'gay team'
DEFAULT_TEAM_NAME_INVITE_USER = 'sad team'
# cmd
CMD_HELP = '/help'
CMD_CREATE_TEAM = '/create_team'
CMD_INVITE_MEMBER = "/invite_member"
CMD_ACCEPT_INVITE = "/accept_invite"
CMD_REJECT_INVITE = "/reject_invite"
# line
LINE_HELP = f"/create_team - to add team\n" \
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
LINE_CREATE_TEAM_ENTER_NAME = "Enter name:"
LINE_CREATE_TEAM_TEAM_CREATED = "team created"
LINE_INVITE_USER_INVITATIONS_WERE_SEND = "Invitations were send"
LINE_INVITE_USER_YOU_WERE_INVITED = "You were invited to team"
LINE_INVITE_USER_BY = "by"
LINE_INVITE_USER_ACCEPT = "accept"
LINE_INVITE_USER_REJECT = "reject"
# pattern
PATTERN_INVITE_USER_TEAM_OPTION = re.compile(rf"{CMD_INVITE_MEMBER}[0-9]+ -- {DEFAULT_TEAM_NAME_INVITE_USER}\n")


def test_help():
    # send help command
    msg = um.UserMessage(
        user_id=DEFAULT_USER_ID_HELP,
        text=CMD_HELP
    )
    responses = list(stub.HandleMessage(msg))
    assert len(responses) == DEFAULT_USER_ID_HELP
    r = responses.pop()
    assert r.user_id == DEFAULT_USER_ID_HELP
    assert r.text == LINE_HELP


def test_create_team():
    # send create team command
    msg = um.UserMessage(
        user_id=DEFAULT_USER_ID_CREATE_TEAM,
        text=CMD_CREATE_TEAM
    )
    responses = list(stub.HandleMessage(msg))
    assert len(responses) == 1
    r = responses.pop()
    assert r.user_id == DEFAULT_USER_ID_CREATE_TEAM
    assert r.text == LINE_CREATE_TEAM_ENTER_NAME
    # send team name
    msg = um.UserMessage(
        user_id=DEFAULT_USER_ID_CREATE_TEAM,
        text=DEFAULT_TEAM_NAME_CREATE_TEAM
    )
    responses = list(stub.HandleMessage(msg))
    assert len(responses) == 2
    r1 = responses.pop()
    assert r1.user_id == DEFAULT_USER_ID_CREATE_TEAM
    assert r1.text == LINE_HELP
    r2 = responses.pop()
    assert r2.user_id == DEFAULT_USER_ID_CREATE_TEAM
    assert r2.text == f"{DEFAULT_TEAM_NAME_CREATE_TEAM} {LINE_CREATE_TEAM_TEAM_CREATED}!"


def test_invite_user():
    # create team
    msg = um.UserMessage(
        user_id=DEFAULT_USER_ID_INVITE_USER,
        text=CMD_CREATE_TEAM
    )
    responses = list(stub.HandleMessage(msg))
    msg = um.UserMessage(
        user_id=DEFAULT_USER_ID_INVITE_USER,
        text=DEFAULT_TEAM_NAME_INVITE_USER
    )
    responses = list(stub.HandleMessage(msg))
    # send invite user command
    msg = um.UserMessage(
        user_id=DEFAULT_USER_ID_INVITE_USER,
        text=CMD_INVITE_MEMBER
    )
    responses = list(stub.HandleMessage(msg))
    assert len(responses) == 1
    r = responses.pop()
    assert r.user_id == DEFAULT_USER_ID_INVITE_USER
    assert PATTERN_INVITE_USER_TEAM_OPTION.match(r.text)
    # send team option
    team_id = r.text
    team_id = re.sub(CMD_INVITE_MEMBER, "", team_id)
    team_id = re.sub(f" -- {DEFAULT_TEAM_NAME_INVITE_USER}\n", "", team_id)
    msg = um.UserMessage(
        user_id=DEFAULT_USER_ID_INVITE_USER,
        text=f"{CMD_INVITE_MEMBER}{team_id}"
    )
    responses = list(stub.HandleMessage(msg))
    assert len(responses) == 1
    r = responses.pop()
    assert r.user_id == DEFAULT_USER_ID_INVITE_USER
    assert r.text == "Tag one or multiple users"
    # send tagged user id
    msg = um.UserMessage(
        user_id=DEFAULT_USER_ID_INVITE_USER,
        text=f"[[{DEFAULT_TAGGED_USER_ID_INVITE_USER}]]"
    )
    responses = list(stub.HandleMessage(msg))
    assert len(responses) == 3
    r1 = responses.pop()
    assert r1.user_id == DEFAULT_USER_ID_INVITE_USER
    assert r1.text == LINE_HELP
    r2 = responses.pop()
    assert r2.user_id == DEFAULT_USER_ID_INVITE_USER
    assert r2.text == LINE_INVITE_USER_INVITATIONS_WERE_SEND
    r3 = responses.pop()
    assert r3.user_id == DEFAULT_TAGGED_USER_ID_INVITE_USER
    assert r3.text == f'{LINE_INVITE_USER_YOU_WERE_INVITED} {DEFAULT_TEAM_NAME_INVITE_USER} {LINE_INVITE_USER_BY} [[{DEFAULT_USER_ID_INVITE_USER}]]\n\n{CMD_ACCEPT_INVITE}{team_id} -- {LINE_INVITE_USER_ACCEPT}\n{CMD_REJECT_INVITE}{team_id} -- {LINE_INVITE_USER_REJECT}'
