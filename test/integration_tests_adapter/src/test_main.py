import grpc
import re

from datetime import datetime, timedelta

import user_message_pb2_grpc as ums
import user_message_pb2 as um

channel = grpc.insecure_channel('frontend-service:50051')
stub = ums.UserMessageHandlerStub(channel)

# user id
DEFAULT_USER_ID_HELP = 1
DEFAULT_TEAM_OWNER_ID_CREATE_TEAM = 2
DEFAULT_TEAM_OWNER_ID_INVITE_TO_TEAM = 3
DEFAULT_INVITED_USER_ID_INVITE_TO_TEAM = 4
DEFAULT_TEAM_OWNER_ID_ACCEPT_TEAM_INVITATION = 5
DEFAULT_INVITED_USER_ID_ACCEPT_TEAM_INVITATION = 6
DEFAULT_TEAM_OWNER_ID_REJECT_TEAM_INVITATION = 7
DEFAULT_INVITED_USER_ID_REJECT_TEAM_INVITATION = 8
DEFAULT_USER_ID_START = 9
DEFAULT_USER_ID_CHANGE_LANGUAGE = 10
DEFAULT_TEAM_OWNER_ID_CREATE_MEETING = 11
DEFAULT_TEAM_OWNER_ID_INVITE_TO_MEETING = 12
DEFAULT_INVITED_USER_ID_INVITE_TO_MEETING = 13
DEFAULT_TEAM_OWNER_ID_ACCEPT_MEETING_INVITATION = 14
DEFAULT_INVITED_USER_ID_ACCEPT_MEETING_INVITATION = 15
DEFAULT_TEAM_OWNER_ID_REJECT_MEETING_INVITATION = 16
DEFAULT_INVITED_USER_ID_REJECT_MEETING_INVITATION = 17
# team name
DEFAULT_TEAM_NAME_CREATE_TEAM = 'gay team'
DEFAULT_TEAM_NAME_INVITE_TO_TEAM = 'sad team'
DEFAULT_TEAM_NAME_ACCEPT_TEAM_INVITATION = 'wide team'
DEFAULT_TEAM_NAME_REJECT_TEAM_INVITATION = 'tight team'
DEFAULT_TEAM_NAME_CREATE_MEETING = 'sleepy team'
DEFAULT_TEAM_NAME_INVITE_TO_MEETING = 'salty team'
DEFAULT_TEAM_NAME_ACCEPT_MEETING_INVITATION = 'random team'
DEFAULT_TEAM_NAME_REJECT_MEETING_INVITATION = 'concrete team'
# meeting desc
DEFAULT_MEETING_DESC_CREATE_MEETING = "gay meeting"
DEFAULT_MEETING_DESC_INVITE_TO_MEETING = "salty meeting"
DEFAULT_MEETING_DESC_ACCEPT_MEETING_INVITATION = "random meeting"
DEFAULT_MEETING_DESC_REJECT_MEETING_INVITATION = "concrete meeting"
# meeting time
DEFAULT_MEETING_TIME_INVALID_CREATE_MEETING = "123 456"
DEFAULT_MEETING_TIME_STR_CREATE_MEETING = "11-11-2022 11:11"
DEFAULT_MEETING_TIME_PARSED_CREATE_MEETING = datetime.strptime(DEFAULT_MEETING_TIME_STR_CREATE_MEETING, '%d-%m-%Y %H:%M')
DEFAULT_MEETING_DATETIME_STR_INVITE_TO_MEETING = "10-10-2022 10:10"
DEFAULT_MEETING_DATETIME_PARSED_INVITE_TO_MEETING = datetime.strptime(DEFAULT_MEETING_DATETIME_STR_INVITE_TO_MEETING, '%d-%m-%Y %H:%M')
DEFAULT_MEETING_DATETIME_STR_ACCEPT_MEETING_INVITATION = "12-12-2022 12:12"
DEFAULT_MEETING_DATETIME_PARSED_ACCEPT_MEETING_INVITATION = datetime.strptime(DEFAULT_MEETING_DATETIME_STR_ACCEPT_MEETING_INVITATION, '%d-%m-%Y %H:%M')
DEFAULT_MEETING_DATETIME_INT_ACCEPT_MEETING_INVITATION = int(DEFAULT_MEETING_DATETIME_PARSED_ACCEPT_MEETING_INVITATION.timestamp())
DEFAULT_MEETING_DATETIME_STR_REJECT_MEETING_INVITATION = "09-09-2022 09:09"
DEFAULT_MEETING_DATETIME_PARSED_REJECT_MEETING_INVITATION = datetime.strptime(DEFAULT_MEETING_DATETIME_STR_REJECT_MEETING_INVITATION, '%d-%m-%Y %H:%M')
# language
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
CMD_CREATE_MEETING = "/create_meeting"
CMD_INVITE_TO_MEETING = "/invite_to_meeting"
CMD_ACCEPT_MEETING_INVITE = "/accept_meeting_invite"
CMD_REJECT_MEETING_INVITE = "/reject_meeting_invite"
CMD_POM = "/pom"
CMD_AOM = "/aom"
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
LINE_CREATE_MEETING_ENTER_DESCRIPTION = "Enter description"
LINE_CREATE_MEETING_ENTER_DATETIME = "Enter datetime (in format DD-MM-YYYY HH:MM)"
LINE_CREATE_MEETING_TRY_AGAIN = "try again!"
LINE_CREATE_MEETING_MEETING_CREATED = "Meeting created"
LINE_INVITE_TO_MEETING_TAG = "Tag one or multiple users"
LINE_INVITING_TO_MEETING_INVITATIONS_SEND = "Invitations to meeting were send"
LINE_INVITING_TO_MEETING_YOU_WERE_INVITED = "You were invited to meeting"
LINE_REJECT_MEETING_INVITATION_REJECTED = "rejected meeting invitation"
LINE_REJECT_MEETING_INVITATION_YOU_REJECTED = "You rejected meeting invitation"
LINE_ACCEPT_MEETING_INVITATION_ACCEPTED = "accepted meeting invitation"
LINE_ACCEPT_MEETING_INVITATION_YOU_ACCEPTED = "You accepted meeting invitation"
LINE_ACCEPT_MEETING_INVITATION_MEETING_STARTS_AT = "meeting starts at"
# team option pattern
PATTERN_TEAM_OPTION_INVITE_TO_TEAM = re.compile(rf"{CMD_INVITE_MEMBER}[0-9]+ -- {DEFAULT_TEAM_NAME_INVITE_TO_TEAM}\n")
PATTERN_TEAM_OPTION_ACCEPT_TEAM_INVITATION = re.compile(rf"{CMD_INVITE_MEMBER}[0-9]+ -- {DEFAULT_TEAM_NAME_ACCEPT_TEAM_INVITATION}\n")
PATTERN_TEAM_OPTION_REJECT_TEAM_INVITATION = re.compile(rf"{CMD_INVITE_MEMBER}[0-9]+ -- {DEFAULT_TEAM_NAME_REJECT_TEAM_INVITATION}\n")
PATTERN_TEAM_OPTION_CREATE_MEETING = re.compile(rf"{CMD_CREATE_MEETING}[0-9]+ -- {DEFAULT_TEAM_NAME_CREATE_MEETING}\n")
PATTERN_TEAM_OPTION_ACCEPT_TEAM_INVITATION_INVITE_TO_MEETING = re.compile(rf"{CMD_INVITE_MEMBER}[0-9]+ -- {DEFAULT_TEAM_NAME_INVITE_TO_MEETING}\n")
PATTERN_TEAM_OPTION_CREATE_MEETING_INVITE_TO_MEETING = re.compile(rf"{CMD_CREATE_MEETING}[0-9]+ -- {DEFAULT_TEAM_NAME_INVITE_TO_MEETING}\n")
PATTERN_TEAM_OPTION_ACCEPT_TEAM_INVITATION_ACCEPT_MEETING_INVITATION = re.compile(rf"{CMD_INVITE_MEMBER}[0-9]+ -- {DEFAULT_TEAM_NAME_ACCEPT_MEETING_INVITATION}\n")
PATTERN_TEAM_OPTION_CREATE_MEETING_ACCEPT_MEETING_INVITATION = re.compile(rf"{CMD_CREATE_MEETING}[0-9]+ -- {DEFAULT_TEAM_NAME_ACCEPT_MEETING_INVITATION}\n")
PATTERN_TEAM_OPTION_ACCEPT_TEAM_INVITATION_REJECT_MEETING_INVITATION = re.compile(rf"{CMD_INVITE_MEMBER}[0-9]+ -- {DEFAULT_TEAM_NAME_REJECT_MEETING_INVITATION}\n")
PATTERN_TEAM_OPTION_CREATE_MEETING_REJECT_MEETING_INVITATION = re.compile(rf"{CMD_CREATE_MEETING}[0-9]+ -- {DEFAULT_TEAM_NAME_REJECT_MEETING_INVITATION}\n")
# meeting option pattern
PATTERN_MEETING_OPTION_INVITE_TO_MEETING_INVITE_TO_MEETING = re.compile(rf"{CMD_INVITE_TO_MEETING}[0-9]+ -- {DEFAULT_MEETING_DESC_INVITE_TO_MEETING}\n")
PATTERN_MEETING_OPTION_INVITE_TO_MEETING_ACCEPT_MEETING_INVITATION = re.compile(rf"{CMD_INVITE_TO_MEETING}[0-9]+ -- {DEFAULT_MEETING_DESC_ACCEPT_MEETING_INVITATION}\n")
PATTERN_MEETING_OPTION_INVITE_TO_MEETING_REJECT_MEETING_INVITATION = re.compile(rf"{CMD_INVITE_TO_MEETING}[0-9]+ -- {DEFAULT_MEETING_DESC_REJECT_MEETING_INVITATION}\n")


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
    _team_owner_id=DEFAULT_TEAM_OWNER_ID_CREATE_TEAM,
    _team_name=DEFAULT_TEAM_NAME_CREATE_TEAM
):
    # send create team command
    msg = um.UserMessage(
        user_id=_team_owner_id,
        text=CMD_CREATE_TEAM
    )
    responses = list(stub.HandleMessage(msg))
    assert len(responses) == 1
    r = responses.pop()
    assert r.user_id == _team_owner_id
    assert r.text == LINE_CREATE_TEAM_ENTER_NAME
    # send team name
    msg = um.UserMessage(
        user_id=_team_owner_id,
        text=_team_name
    )
    responses = list(stub.HandleMessage(msg))
    assert len(responses) == 2
    r1 = responses.pop()
    assert r1.user_id == _team_owner_id
    assert r1.text == LINE_HELP_EN
    r2 = responses.pop()
    assert r2.user_id == _team_owner_id
    assert r2.text == f"{_team_name} {LINE_CREATE_TEAM_TEAM_CREATED}!"


def test_invite_to_team(
    _team_owner_id=DEFAULT_TEAM_OWNER_ID_INVITE_TO_TEAM,
    _team_name=DEFAULT_TEAM_NAME_INVITE_TO_TEAM,
    _team_option_pattern=PATTERN_TEAM_OPTION_INVITE_TO_TEAM,
    _invited_user_id=DEFAULT_INVITED_USER_ID_INVITE_TO_TEAM
) -> str:
    # create team
    test_create_team(
        _team_owner_id=_team_owner_id,
        _team_name=_team_name
    )
    # send invite user command
    msg = um.UserMessage(
        user_id=_team_owner_id,
        text=CMD_INVITE_MEMBER
    )
    responses = list(stub.HandleMessage(msg))
    assert len(responses) == 1
    r = responses.pop()
    assert r.user_id == _team_owner_id
    assert _team_option_pattern.match(r.text)
    # send team option
    team_id = r.text
    team_id = re.sub(CMD_INVITE_MEMBER, "", team_id)
    team_id = re.sub(f" -- {_team_name}\n", "", team_id)
    msg = um.UserMessage(
        user_id=_team_owner_id,
        text=f"{CMD_INVITE_MEMBER}{team_id}"
    )
    responses = list(stub.HandleMessage(msg))
    assert len(responses) == 1
    r = responses.pop()
    assert r.user_id == _team_owner_id
    assert r.text == "Tag one or multiple users"
    # send tagged user id
    msg = um.UserMessage(
        user_id=_team_owner_id,
        text=f"[[{_invited_user_id}]]"
    )
    responses = list(stub.HandleMessage(msg))
    assert len(responses) == 3
    r1 = responses.pop()
    assert r1.user_id == _team_owner_id
    assert r1.text == LINE_HELP_EN
    r2 = responses.pop()
    assert r2.user_id == _team_owner_id
    assert r2.text == LINE_INVITE_USER_INVITATIONS_WERE_SEND
    r3 = responses.pop()
    assert r3.user_id == _invited_user_id
    assert r3.text == f'{LINE_INVITE_USER_YOU_WERE_INVITED} {_team_name} {LINE_INVITE_USER_BY} [[{_team_owner_id}]]\n\n{CMD_ACCEPT_INVITE}{team_id} -- {LINE_INVITE_USER_ACCEPT}\n{CMD_REJECT_INVITE}{team_id} -- {LINE_INVITE_USER_REJECT}'
    return team_id


def test_accept_team_invitation(
    _user_id=DEFAULT_TEAM_OWNER_ID_ACCEPT_TEAM_INVITATION,
    _team_name=DEFAULT_TEAM_NAME_ACCEPT_TEAM_INVITATION,
    _team_option_pattern=PATTERN_TEAM_OPTION_ACCEPT_TEAM_INVITATION,
    _invited_user_id=DEFAULT_INVITED_USER_ID_ACCEPT_TEAM_INVITATION
) -> str:
    # invite user
    team_id = test_invite_to_team(
        _team_owner_id=_user_id,
        _team_name=_team_name,
        _team_option_pattern=_team_option_pattern,
        _invited_user_id=_invited_user_id
    )
    # send accept invitation command
    msg = um.UserMessage(
        user_id=_invited_user_id,
        text=f"{CMD_ACCEPT_INVITE}{team_id}"
    )
    responses = list(stub.HandleMessage(msg))
    assert len(responses) == 2
    r1 = responses.pop()
    assert r1.user_id == _user_id
    assert r1.text == f"[[{_invited_user_id}]] {LINE_ACCEPT_INVITATION_ACCEPTED_INVITATION}"
    r2 = responses.pop()
    assert r2.user_id == _invited_user_id
    assert r2.text == f"{LINE_ACCEPT_INVITATION_ACCEPTED}!"
    return team_id


def test_reject_team_invitation(
    _user_id=DEFAULT_TEAM_OWNER_ID_REJECT_TEAM_INVITATION,
    _team_name=DEFAULT_TEAM_NAME_REJECT_TEAM_INVITATION,
    _team_option_pattern=PATTERN_TEAM_OPTION_REJECT_TEAM_INVITATION,
    _invited_user_id=DEFAULT_INVITED_USER_ID_REJECT_TEAM_INVITATION
):
    # invite user
    team_id = test_invite_to_team(
        _team_owner_id=_user_id,
        _team_name=_team_name,
        _team_option_pattern=_team_option_pattern,
        _invited_user_id=_invited_user_id
    )
    # send reject invitation command
    msg = um.UserMessage(
        user_id=_invited_user_id,
        text=f"{CMD_REJECT_INVITE}{team_id}"
    )
    responses = list(stub.HandleMessage(msg))
    assert len(responses) == 2
    r1 = responses.pop()
    assert r1.user_id == _user_id
    assert r1.text == f"[[{_invited_user_id}]] {LINE_REJECT_INVITATION_REJECTED_INVITATION}"
    r2 = responses.pop()
    assert r2.user_id == _invited_user_id
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


def test_create_meeting(
    _team_owner_id=DEFAULT_TEAM_OWNER_ID_CREATE_MEETING,
    _team_name=DEFAULT_TEAM_NAME_CREATE_MEETING,
    _team_option_pattern=PATTERN_TEAM_OPTION_CREATE_MEETING,
    _meeting_datetime_invalid=DEFAULT_MEETING_TIME_INVALID_CREATE_MEETING,
    _meeting_datetime_str=DEFAULT_MEETING_TIME_STR_CREATE_MEETING,
    _meeting_datetime_parsed=DEFAULT_MEETING_TIME_PARSED_CREATE_MEETING,
    _meeting_desc=DEFAULT_MEETING_DESC_CREATE_MEETING
):
    # create team
    test_create_team(
        _team_owner_id=_team_owner_id,
        _team_name=_team_name
    )
    # send create meeting command
    msg = um.UserMessage(
        user_id=_team_owner_id,
        text=CMD_CREATE_MEETING
    )
    responses = list(stub.HandleMessage(msg))
    assert len(responses) == 1
    r = responses.pop()
    assert r.user_id == _team_owner_id
    assert _team_option_pattern.match(r.text)
    # send team option
    team_id = r.text
    team_id = re.sub(CMD_CREATE_MEETING, "", team_id)
    team_id = re.sub(f" -- {_team_name}\n", "", team_id)
    msg = um.UserMessage(
        user_id=_team_owner_id,
        text=f"{CMD_CREATE_MEETING}{team_id}"
    )
    responses = list(stub.HandleMessage(msg))
    assert len(responses) == 1
    r = responses.pop()
    assert r.user_id == _team_owner_id
    assert r.text == f"{LINE_CREATE_MEETING_ENTER_DESCRIPTION}:"
    # send meeting description
    msg = um.UserMessage(
        user_id=_team_owner_id,
        text=_meeting_desc
    )
    responses = list(stub.HandleMessage(msg))
    assert len(responses) == 1
    r = responses.pop()
    assert r.user_id == _team_owner_id
    assert r.text == f"{LINE_CREATE_MEETING_ENTER_DATETIME}:"
    # send invalid meeting datetime
    msg = um.UserMessage(
        user_id=_team_owner_id,
        text=_meeting_datetime_invalid
    )
    responses = list(stub.HandleMessage(msg))
    assert len(responses) == 1
    r = responses.pop()
    assert r.user_id == _team_owner_id
    assert r.text == LINE_CREATE_MEETING_TRY_AGAIN
    # send valid meeting datetime
    msg = um.UserMessage(
        user_id=_team_owner_id,
        text=_meeting_datetime_str
    )
    responses = list(stub.HandleMessage(msg))
    assert len(responses) == 2
    r1 = responses.pop()
    assert r1.user_id == _team_owner_id
    assert r1.text == f"{_meeting_desc} in T - 5!"
    assert r1.timestamp == int((_meeting_datetime_parsed - timedelta(minutes=5)).timestamp())
    r2 = responses.pop()
    assert r2.user_id == _team_owner_id
    assert r2.text == f"{LINE_CREATE_MEETING_MEETING_CREATED}!"


def test_invite_to_meeting(
    _team_owner_id=DEFAULT_TEAM_OWNER_ID_INVITE_TO_MEETING,
    _invited_user_id=DEFAULT_INVITED_USER_ID_INVITE_TO_MEETING,
    _team_name=DEFAULT_TEAM_NAME_INVITE_TO_MEETING,
    _team_option_pattern_accept_team_invitation=PATTERN_TEAM_OPTION_ACCEPT_TEAM_INVITATION_INVITE_TO_MEETING,
    _team_option_pattern_create_meeting=PATTERN_TEAM_OPTION_CREATE_MEETING_INVITE_TO_MEETING,
    _meeting_desc=DEFAULT_MEETING_DESC_INVITE_TO_MEETING,
    _meeting_datetime_str=DEFAULT_MEETING_DATETIME_STR_INVITE_TO_MEETING,
    _meeting_datetime_parsed=DEFAULT_MEETING_DATETIME_PARSED_INVITE_TO_MEETING,
    _meeting_option_pattern_invite_to_meeting=PATTERN_MEETING_OPTION_INVITE_TO_MEETING_INVITE_TO_MEETING
) -> str:
    # create team, invite user, make user accept
    team_id = test_accept_team_invitation(
        _user_id=_team_owner_id,
        _team_name=_team_name,
        _team_option_pattern=_team_option_pattern_accept_team_invitation,
        _invited_user_id=_invited_user_id
    )
    # send create meeting command
    msg = um.UserMessage(
        user_id=_team_owner_id,
        text=CMD_CREATE_MEETING
    )
    responses = list(stub.HandleMessage(msg))
    assert len(responses) == 1
    r = responses.pop()
    assert r.user_id == _team_owner_id
    assert _team_option_pattern_create_meeting.match(r.text)
    # send team option
    team_id = r.text
    team_id = re.sub(CMD_CREATE_MEETING, "", team_id)
    team_id = re.sub(f" -- {_team_name}\n", "", team_id)
    msg = um.UserMessage(
        user_id=_team_owner_id,
        text=f"{CMD_CREATE_MEETING}{team_id}"
    )
    responses = list(stub.HandleMessage(msg))
    assert len(responses) == 1
    r = responses.pop()
    assert r.user_id == _team_owner_id
    assert r.text == f"{LINE_CREATE_MEETING_ENTER_DESCRIPTION}:"
    # send meeting description
    msg = um.UserMessage(
        user_id=_team_owner_id,
        text=_meeting_desc
    )
    responses = list(stub.HandleMessage(msg))
    assert len(responses) == 1
    r = responses.pop()
    assert r.user_id == _team_owner_id
    assert r.text == f"{LINE_CREATE_MEETING_ENTER_DATETIME}:"
    # send valid meeting datetime
    msg = um.UserMessage(
        user_id=_team_owner_id,
        text=_meeting_datetime_str
    )
    responses = list(stub.HandleMessage(msg))
    assert len(responses) == 2
    r1 = responses.pop()
    assert r1.user_id == _team_owner_id
    assert r1.text == f"{_meeting_desc} in T - 5!"
    assert r1.timestamp == int((_meeting_datetime_parsed - timedelta(minutes=5)).timestamp())
    r2 = responses.pop()
    assert r2.user_id == _team_owner_id
    assert r2.text == f"{LINE_CREATE_MEETING_MEETING_CREATED}!"
    # send invite to meeting command
    msg = um.UserMessage(
        user_id=_team_owner_id,
        text=CMD_INVITE_TO_MEETING
    )
    responses = list(stub.HandleMessage(msg))
    assert len(responses) == 1
    r = responses.pop()
    assert r.user_id == _team_owner_id
    assert _meeting_option_pattern_invite_to_meeting.match(r.text)
    # send meeting option
    meeting_id = r.text
    meeting_id = re.sub(CMD_INVITE_TO_MEETING, "", meeting_id)
    meeting_id = re.sub(f" -- {_meeting_desc}\n", "", meeting_id)
    msg = um.UserMessage(
        user_id=_team_owner_id,
        text=f"{CMD_INVITE_TO_MEETING}{meeting_id}"
    )
    responses = list(stub.HandleMessage(msg))
    assert len(responses) == 1
    r = responses.pop()
    assert r.user_id == _team_owner_id
    assert r.text == LINE_INVITE_TO_MEETING_TAG
    # send invited user id
    msg = um.UserMessage(
        user_id=_team_owner_id,
        text=f"[[{_invited_user_id}]]"
    )
    responses = list(stub.HandleMessage(msg))
    assert len(responses) == 3
    r1 = responses.pop()
    assert r1.user_id == _team_owner_id
    assert r1.text == LINE_HELP_EN
    r2 = responses.pop()
    assert r2.user_id == _team_owner_id
    assert r2.text == LINE_INVITING_TO_MEETING_INVITATIONS_SEND
    r3 = responses.pop()
    assert r3.user_id == _invited_user_id
    assert r3.text == f'{LINE_INVITING_TO_MEETING_YOU_WERE_INVITED} {_meeting_desc} by [[{_team_owner_id}]]\n\n{CMD_ACCEPT_MEETING_INVITE}{meeting_id} -- accept\n{CMD_REJECT_MEETING_INVITE}{meeting_id} -- reject'
    return meeting_id


def test_accept_invite_to_meeting(
        _team_owner_id=DEFAULT_TEAM_OWNER_ID_ACCEPT_MEETING_INVITATION,
        _invited_user_id=DEFAULT_INVITED_USER_ID_ACCEPT_MEETING_INVITATION,
        _team_name=DEFAULT_TEAM_NAME_ACCEPT_MEETING_INVITATION,
        _team_option_pattern_accept_team_invitation=PATTERN_TEAM_OPTION_ACCEPT_TEAM_INVITATION_ACCEPT_MEETING_INVITATION,
        _team_option_pattern_create_meeting=PATTERN_TEAM_OPTION_CREATE_MEETING_ACCEPT_MEETING_INVITATION,
        _meeting_desc=DEFAULT_MEETING_DESC_ACCEPT_MEETING_INVITATION,
        _meeting_datetime_str=DEFAULT_MEETING_DATETIME_STR_ACCEPT_MEETING_INVITATION,
        _meeting_datetime_parsed=DEFAULT_MEETING_DATETIME_PARSED_ACCEPT_MEETING_INVITATION,
        _meeting_option_pattern_invite_to_meeting=PATTERN_MEETING_OPTION_INVITE_TO_MEETING_ACCEPT_MEETING_INVITATION
):
    meeting_id = test_invite_to_meeting(
        _team_owner_id=_team_owner_id,
        _invited_user_id=_invited_user_id,
        _team_name=_team_name,
        _team_option_pattern_accept_team_invitation=_team_option_pattern_accept_team_invitation,
        _team_option_pattern_create_meeting=_team_option_pattern_create_meeting,
        _meeting_desc=_meeting_desc,
        _meeting_datetime_str=_meeting_datetime_str,
        _meeting_datetime_parsed=_meeting_datetime_parsed,
        _meeting_option_pattern_invite_to_meeting=_meeting_option_pattern_invite_to_meeting
    )
    # send accept meeting invite command
    msg = um.UserMessage(
        user_id=_invited_user_id,
        text=f"{CMD_ACCEPT_MEETING_INVITE}{meeting_id}"
    )
    responses = list(stub.HandleMessage(msg))
    assert len(responses) == 4
    r1 = responses.pop()
    assert r1.user_id == _team_owner_id
    assert r1.text == f'[[{_invited_user_id}]] {LINE_ACCEPT_MEETING_INVITATION_ACCEPTED}'
    r2 = responses.pop()
    assert r2.user_id == _invited_user_id
    meeting_date = datetime.fromtimestamp(DEFAULT_MEETING_DATETIME_INT_ACCEPT_MEETING_INVITATION)
    assert r2.text == f'{_meeting_desc} {LINE_ACCEPT_MEETING_INVITATION_MEETING_STARTS_AT} {meeting_date}'
    r3 = responses.pop()
    assert r3.user_id == _invited_user_id
    assert r3.text == f'{LINE_ACCEPT_MEETING_INVITATION_YOU_ACCEPTED}'
    r4 = responses.pop()
    assert r4.user_id == _invited_user_id
    assert r4.text == f'{_meeting_desc} in T - 5!\n\n{CMD_POM}{meeting_id} -- heading!\n{CMD_AOM}{meeting_id} -- ignore'


def test_reject_invite_to_meeting(
        _team_owner_id=DEFAULT_TEAM_OWNER_ID_REJECT_MEETING_INVITATION,
        _invited_user_id=DEFAULT_INVITED_USER_ID_REJECT_MEETING_INVITATION,
        _team_name=DEFAULT_TEAM_NAME_REJECT_MEETING_INVITATION,
        _team_option_pattern_accept_team_invitation=PATTERN_TEAM_OPTION_ACCEPT_TEAM_INVITATION_REJECT_MEETING_INVITATION,
        _team_option_pattern_create_meeting=PATTERN_TEAM_OPTION_CREATE_MEETING_REJECT_MEETING_INVITATION,
        _meeting_desc=DEFAULT_MEETING_DESC_REJECT_MEETING_INVITATION,
        _meeting_datetime_str=DEFAULT_MEETING_DATETIME_STR_REJECT_MEETING_INVITATION,
        _meeting_datetime_parsed=DEFAULT_MEETING_DATETIME_PARSED_REJECT_MEETING_INVITATION,
        _meeting_option_pattern_invite_to_meeting=PATTERN_MEETING_OPTION_INVITE_TO_MEETING_REJECT_MEETING_INVITATION
):
    meeting_id = test_invite_to_meeting(
        _team_owner_id=_team_owner_id,
        _invited_user_id=_invited_user_id,
        _team_name=_team_name,
        _team_option_pattern_accept_team_invitation=_team_option_pattern_accept_team_invitation,
        _team_option_pattern_create_meeting=_team_option_pattern_create_meeting,
        _meeting_desc=_meeting_desc,
        _meeting_datetime_str=_meeting_datetime_str,
        _meeting_datetime_parsed=_meeting_datetime_parsed,
        _meeting_option_pattern_invite_to_meeting=_meeting_option_pattern_invite_to_meeting
    )
    # send reject meeting invite command
    msg = um.UserMessage(
        user_id=_invited_user_id,
        text=f"{CMD_REJECT_MEETING_INVITE}{meeting_id}"
    )
    responses = list(stub.HandleMessage(msg))
    assert len(responses) == 2
    r1 = responses.pop()
    assert r1.user_id == _team_owner_id
    assert r1.text == f'[[{_invited_user_id}]] {LINE_REJECT_MEETING_INVITATION_REJECTED}'
    r2 = responses.pop()
    assert r2.user_id == _invited_user_id
    assert r2.text == LINE_REJECT_MEETING_INVITATION_YOU_REJECTED
