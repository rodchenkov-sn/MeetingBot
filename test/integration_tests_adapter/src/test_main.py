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
DEFAULT_USER_ID_ACCEPT_INVITATION = 5
DEFAULT_TAGGED_USER_ID_ACCEPT_INVITATION = 6
DEFAULT_USER_ID_REJECT_INVITATION = 7
DEFAULT_TAGGED_USER_ID_REJECT_INVITATION = 8
DEFAULT_USER_ID_START = 9
DEFAULT_USER_ID_CHANGE_LANGUAGE = 10
# team name
DEFAULT_TEAM_NAME_CREATE_TEAM = 'gay team'
DEFAULT_TEAM_NAME_INVITE_USER = 'sad team'
DEFAULT_TEAM_NAME_ACCEPT_INVITATION = 'wide team'
DEFAULT_TEAM_NAME_REJECT_INVITATION = 'tight team'
#language
DEFAULT_LANGUAGE_NAME_EN = 'en'
DEFAULT_LANGUAGE_NAME_RU = 'ru'
# cmd
CMD_HELP = '/help'
CMD_CREATE_TEAM = '/create_team'
CMD_INVITE_MEMBER = "/invite_member"
CMD_ACCEPT_INVITE = "/accept_invite"
CMD_REJECT_INVITE = "/reject_invite"
CMD_START = "/start"
CMD_CHANGE_LANGUAGE = "/change_language"
# line
LINE_HELP_EN = f"/create_team - to add team\n" \
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
LINE_HELP_RU = f"/create_team - чтобы добавить команду\n" \
    f"/invite_member - чтобы пригласить пользователя\n" \
    f"/create_meeting - чтобы создать встречу\n" \
    f"/invite_to_meeting - чтобы пригласить на встречу\n" \
    f"/add_child_team - чтобы добавить дочернюю команду\n" \
    f"/edit_policy - чтобы редактировать политику команды\n" \
    f"/add_to_meeting - чтобы добавить на встречу\n" \
    f"/update_meeting_time - чтобы обновить время встречи\n" \
    f"/get_agenda - чтобы получить расписание\n" \
    f"/upload_file - чтобы загрузить файл\n" \
    f"/get_files - чтобы получить доступные файлы\n" \
    f"/auth_gcal - чтобы авторизоваться используя гугл календарь\n" \
    f"/change_language - чтобы сменить язык\n" \
    f"\n/help - чтобы увидеть это сообщение"
LINE_CREATE_TEAM_ENTER_NAME = "Enter name:"
LINE_CREATE_TEAM_TEAM_CREATED = "team created"
LINE_INVITE_USER_INVITATIONS_WERE_SEND = "Invitations were send"
LINE_INVITE_USER_YOU_WERE_INVITED = "You were invited to team"
LINE_INVITE_USER_BY = "by"
LINE_INVITE_USER_ACCEPT = "accept"
LINE_INVITE_USER_REJECT = "reject"
LINE_ACCEPT_INVITATION_ACCEPTED = "Accepted"
LINE_REJECT_INVITATION_REJECTED = "Rejected"
LINE_ACCEPT_INVITATION_ACCEPTED_INVITATION = "accepted your invitation"
LINE_REJECT_INVITATION_REJECTED_INVITATION = "rejected your invitation"
LINE_CHANGE_LANGUAGE_EN_NAME_EN = "English"
LINE_CHANGE_LANGUAGE_EN_NAME_RU = "Английский"
LINE_CHANGE_LANGUAGE_RU_NAME_EN = "Russian"
LINE_CHANGE_LANGUAGE_RU_NAME_RU = "Русский"
LINE_CHANGE_LANGUAGE_CHANGED_EN = "Language changed"
LINE_CHANGE_LANGUAGE_CHANGED_RU = "Язык сменен"
# pattern
PATTERN_TEAM_OPTION_INVITE_USER = re.compile(rf"{CMD_INVITE_MEMBER}[0-9]+ -- {DEFAULT_TEAM_NAME_INVITE_USER}\n")
PATTERN_TEAM_OPTION_ACCEPT_INVITATION = re.compile(rf"{CMD_INVITE_MEMBER}[0-9]+ -- {DEFAULT_TEAM_NAME_ACCEPT_INVITATION}\n")
PATTERN_TEAM_OPTION_REJECT_INVITATION = re.compile(rf"{CMD_INVITE_MEMBER}[0-9]+ -- {DEFAULT_TEAM_NAME_REJECT_INVITATION}\n")


def test_help(
    _user_id=DEFAULT_USER_ID_HELP,
    _line_help=LINE_HELP_EN
):
    # send help command
    msg = um.UserMessage(
        user_id=_user_id,
        text=CMD_HELP
    )
    responses = list(stub.HandleMessage(msg))
    assert len(responses) == 1
    r = responses.pop()
    assert r.user_id == _user_id
    assert r.text == _line_help


def test_create_team(
    _user_id=DEFAULT_USER_ID_CREATE_TEAM,
    _team_name=DEFAULT_TEAM_NAME_CREATE_TEAM
):
    # send create team command
    msg = um.UserMessage(
        user_id=_user_id,
        text=CMD_CREATE_TEAM
    )
    responses = list(stub.HandleMessage(msg))
    assert len(responses) == 1
    r = responses.pop()
    assert r.user_id == _user_id
    assert r.text == LINE_CREATE_TEAM_ENTER_NAME
    # send team name
    msg = um.UserMessage(
        user_id=_user_id,
        text=_team_name
    )
    responses = list(stub.HandleMessage(msg))
    assert len(responses) == 2
    r1 = responses.pop()
    assert r1.user_id == _user_id
    assert r1.text == LINE_HELP_EN
    r2 = responses.pop()
    assert r2.user_id == _user_id
    assert r2.text == f"{_team_name} {LINE_CREATE_TEAM_TEAM_CREATED}!"


def test_invite_user(
    _user_id=DEFAULT_USER_ID_INVITE_USER,
    _team_name=DEFAULT_TEAM_NAME_INVITE_USER,
    _team_option_pattern=PATTERN_TEAM_OPTION_INVITE_USER,
    _tagged_user_id=DEFAULT_TAGGED_USER_ID_INVITE_USER
) -> str:
    # create team
    test_create_team(
        _user_id=_user_id,
        _team_name=_team_name
    )
    # send invite user command
    msg = um.UserMessage(
        user_id=_user_id,
        text=CMD_INVITE_MEMBER
    )
    responses = list(stub.HandleMessage(msg))
    assert len(responses) == 1
    r = responses.pop()
    assert r.user_id == _user_id
    assert _team_option_pattern.match(r.text)
    # send team option
    team_id = r.text
    team_id = re.sub(CMD_INVITE_MEMBER, "", team_id)
    team_id = re.sub(f" -- {_team_name}\n", "", team_id)
    msg = um.UserMessage(
        user_id=_user_id,
        text=f"{CMD_INVITE_MEMBER}{team_id}"
    )
    responses = list(stub.HandleMessage(msg))
    assert len(responses) == 1
    r = responses.pop()
    assert r.user_id == _user_id
    assert r.text == "Tag one or multiple users"
    # send tagged user id
    msg = um.UserMessage(
        user_id=_user_id,
        text=f"[[{_tagged_user_id}]]"
    )
    responses = list(stub.HandleMessage(msg))
    assert len(responses) == 3
    r1 = responses.pop()
    assert r1.user_id == _user_id
    assert r1.text == LINE_HELP_EN
    r2 = responses.pop()
    assert r2.user_id == _user_id
    assert r2.text == LINE_INVITE_USER_INVITATIONS_WERE_SEND
    r3 = responses.pop()
    assert r3.user_id == _tagged_user_id
    assert r3.text == f'{LINE_INVITE_USER_YOU_WERE_INVITED} {_team_name} {LINE_INVITE_USER_BY} [[{_user_id}]]\n\n{CMD_ACCEPT_INVITE}{team_id} -- {LINE_INVITE_USER_ACCEPT}\n{CMD_REJECT_INVITE}{team_id} -- {LINE_INVITE_USER_REJECT}'
    return team_id


def test_accept_invitation(
    _user_id=DEFAULT_USER_ID_ACCEPT_INVITATION,
    _team_name=DEFAULT_TEAM_NAME_ACCEPT_INVITATION,
    _team_option_pattern=PATTERN_TEAM_OPTION_ACCEPT_INVITATION,
    _tagged_user_id=DEFAULT_TAGGED_USER_ID_ACCEPT_INVITATION
):
    # invite user
    team_id = test_invite_user(
        _user_id=_user_id,
        _team_name=_team_name,
        _team_option_pattern=_team_option_pattern,
        _tagged_user_id=_tagged_user_id
    )
    # send accept invitation command
    msg = um.UserMessage(
        user_id=_tagged_user_id,
        text=f"{CMD_ACCEPT_INVITE}{team_id}"
    )
    responses = list(stub.HandleMessage(msg))
    assert len(responses) == 2
    r1 = responses.pop()
    assert r1.user_id == _user_id
    assert r1.text == f"[[{_tagged_user_id}]] {LINE_ACCEPT_INVITATION_ACCEPTED_INVITATION}"
    r2 = responses.pop()
    assert r2.user_id == _tagged_user_id
    assert r2.text == f"{LINE_ACCEPT_INVITATION_ACCEPTED}!"


def test_reject_invitation(
    _user_id=DEFAULT_USER_ID_REJECT_INVITATION,
    _team_name=DEFAULT_TEAM_NAME_REJECT_INVITATION,
    _team_option_pattern=PATTERN_TEAM_OPTION_REJECT_INVITATION,
    _tagged_user_id=DEFAULT_TAGGED_USER_ID_REJECT_INVITATION
):
    # invite user
    team_id = test_invite_user(
        _user_id=_user_id,
        _team_name=_team_name,
        _team_option_pattern=_team_option_pattern,
        _tagged_user_id=_tagged_user_id
    )
    # send reject invitation command
    msg = um.UserMessage(
        user_id=_tagged_user_id,
        text=f"{CMD_REJECT_INVITE}{team_id}"
    )
    responses = list(stub.HandleMessage(msg))
    assert len(responses) == 2
    r1 = responses.pop()
    assert r1.user_id == _user_id
    assert r1.text == f"[[{_tagged_user_id}]] {LINE_REJECT_INVITATION_REJECTED_INVITATION}"
    r2 = responses.pop()
    assert r2.user_id == _tagged_user_id
    assert r2.text == f"{LINE_REJECT_INVITATION_REJECTED}!"


def test_start(
    _user_id=DEFAULT_USER_ID_START,
    _line_help=LINE_HELP_EN
):
    # send start command
    msg = um.UserMessage(
        user_id=_user_id,
        text=CMD_START
    )
    responses = list(stub.HandleMessage(msg))
    assert len(responses) == 1
    r = responses.pop()
    assert r.user_id == _user_id
    assert r.text == _line_help


def test_change_language(
    _user_id=DEFAULT_USER_ID_CHANGE_LANGUAGE,
    _lang_name_before=DEFAULT_LANGUAGE_NAME_EN,
    _lang_name_after=DEFAULT_LANGUAGE_NAME_RU,
    _lang_line_before=LINE_CHANGE_LANGUAGE_EN_NAME_EN,
    _lang_line_after=LINE_CHANGE_LANGUAGE_RU_NAME_EN,
    _line_help_before=LINE_HELP_EN,
    _line_help_after=LINE_HELP_RU,
    _line_change_lang_changed=LINE_CHANGE_LANGUAGE_CHANGED_RU,
):
    # test help command
    test_help(_user_id=_user_id, _line_help=_line_help_before)
    # send change language command
    msg = um.UserMessage(
        user_id=_user_id,
        text=CMD_CHANGE_LANGUAGE
    )
    rmsg = [
        f"{CMD_CHANGE_LANGUAGE}__{_lang_name_before} -- {_lang_line_before}\n",
        f"{CMD_CHANGE_LANGUAGE}__{_lang_name_after} -- {_lang_line_after}\n"
    ]
    responses = list(stub.HandleMessage(msg))
    assert len(responses) == 2
    r1 = responses.pop()
    assert r1.user_id == _user_id
    assert r1.text in rmsg
    r2 = responses.pop()
    assert r2.user_id == _user_id
    assert r2.text in rmsg
    # send language option
    msg = um.UserMessage(
        user_id=_user_id,
        text=f"{CMD_CHANGE_LANGUAGE}__{_lang_name_after}"
    )
    responses = list(stub.HandleMessage(msg))
    assert len(responses) == 2
    r1 = responses.pop()
    assert r1.user_id == _user_id
    assert r1.text == _line_help_after
    r2 = responses.pop()
    assert r2.user_id == _user_id
    assert r2.text == _line_change_lang_changed
