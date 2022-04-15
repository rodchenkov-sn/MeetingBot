import pytest

import re

from server import start_server, stop_server, Client, responses_queue

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

USER_ID_1 = 1
USER_ID_2 = 2
USER_ID_3 = 3
USER_ID_4 = 4
USER_ID_5 = 5
USER_ID_6 = 6
USER_ID_7 = 7
USER_ID_8 = 8
USER_ID_9 = 9
USER_ID_10 = 10
USER_ID_11 = 11

USERNAME_1 = "Ayanami"
USERNAME_2 = "Rudy"
USERNAME_3 = "Asuna"
USERNAME_4 = "Sakura"
USERNAME_5 = "Rosy"
USERNAME_6 = "Cinderella"
USERNAME_7 = "Katya"
USERNAME_8 = "Nastya"
USERNAME_9 = "Miya"
USERNAME_10 = "Koya"
USERNAME_11 = "Annie"


def create_team(
    username,
    user_id,
    team_name
):
    client = Client(username, user_id)

    client.send_message('/create_team')
    resp = responses_queue.get(timeout=10)
    assert resp.user_id == user_id
    assert resp.text == "Enter name:"

    client.send_message(team_name)
    resp = responses_queue.get(timeout=10)
    assert resp.user_id == user_id
    assert resp.text == f"{team_name} team created!"
    resp = responses_queue.get(timeout=10)
    assert resp.user_id == user_id
    assert resp.text == LINE_HELP_EN


def invite_to_team(
    username,
    user_id,
    team_name,
    invited_username,
    invited_user_id
) -> str:
    pattern_team_id = re.compile(rf"/invite_member[0-9]+ -- {team_name}\n")

    create_team(
        username,
        user_id,
        team_name
    )

    client = Client(username, user_id)
    invited_client = Client(invited_username, invited_user_id)

    client.send_message("/invite_member")
    resp = responses_queue.get(timeout=10)
    assert resp.user_id == user_id
    assert pattern_team_id.match(resp.text)

    team_id = resp.text
    team_id = re.sub("/invite_member", "", team_id)
    team_id = re.sub(f" -- {team_name}\n", "", team_id)

    client.send_message(f"/invite_member{team_id}")
    resp = responses_queue.get(timeout=10)
    assert resp.user_id == user_id
    assert resp.text == "Tag one or multiple users"

    client.send_message(f"@{invited_username}")
    resp = responses_queue.get(timeout=10)
    assert resp.user_id == invited_user_id
    assert resp.text == f'You were invited to team {team_name} by @{username}\n\n/accept_invite{team_id} -- accept\n/reject_invite{team_id} -- reject'
    resp = responses_queue.get(timeout=10)
    assert resp.user_id == user_id
    assert resp.text == "Invitations were send"
    resp = responses_queue.get(timeout=10)
    assert resp.user_id == user_id
    assert resp.text == LINE_HELP_EN

    return team_id


def accept_team_invite(
    username,
    user_id,
    team_name,
    invited_username,
    invited_user_id
):
    team_id = invite_to_team(
        username,
        user_id,
        team_name,
        invited_username,
        invited_user_id
    )

    invited_client = Client(invited_username, invited_user_id)

    invited_client.send_message(f"/accept_invite{team_id}")
    resp = responses_queue.get(timeout=10)
    assert resp.user_id == invited_user_id
    assert resp.text == "Accepted!"
    resp = responses_queue.get(timeout=10)
    assert resp.user_id == user_id
    assert resp.text == f"@{invited_username} accepted your invitation"


def reject_team_invite(
    username,
    user_id,
    team_name,
    invited_username,
    invited_user_id
):
    team_id = invite_to_team(
        username,
        user_id,
        team_name,
        invited_username,
        invited_user_id
    )

    invited_client = Client(invited_username, invited_user_id)

    invited_client.send_message(f"/reject_invite{team_id}")
    resp = responses_queue.get(timeout=10)
    assert resp.user_id == invited_user_id
    assert resp.text == "Rejected!"
    resp = responses_queue.get(timeout=10)
    assert resp.user_id == user_id
    assert resp.text == f"@{invited_username} rejected your invitation"


def create_meeting(
    username,
    user_id,
    team_name,
    meeting_desc,
    meeting_time_str
):
    pattern_team_id = re.compile(rf"/create_meeting[0-9]+ -- {team_name}\n")

    create_team(
        username,
        user_id,
        team_name
    )

    client = Client(username, user_id)

    client.send_message('/create_meeting')
    resp = responses_queue.get(timeout=10)
    assert resp.user_id == user_id
    assert pattern_team_id.match(resp.text)

    team_id = resp.text
    team_id = re.sub("/create_meeting", "", team_id)
    team_id = re.sub(f" -- {team_name}\n", "", team_id)

    client.send_message(f"/create_meeting{team_id}")
    resp = responses_queue.get(timeout=10)
    assert resp.user_id == user_id
    assert resp.text == "Enter description:"

    client.send_message(meeting_desc)
    resp = responses_queue.get(timeout=10)
    assert resp.user_id == user_id
    assert resp.text == "Enter datetime (in format DD-MM-YYYY HH:MM):"

    client.send_message(meeting_time_str)
    resp = responses_queue.get(timeout=10)
    assert resp.user_id == user_id
    assert resp.text == "Meeting created!"


@pytest.fixture(scope='session', autouse=True)
def serv_starter():
    start_server()
    yield True
    stop_server()


def test_help_cmd(serv_starter):
    user_id = USER_ID_1
    client = Client(USERNAME_1, user_id)

    client.send_message('/help')
    resp = responses_queue.get(timeout=10)
    assert resp.user_id == user_id
    assert resp.text == LINE_HELP_EN


def test_start_cmd(serv_starter):
    user_id = USER_ID_2
    client = Client(USERNAME_2, user_id)

    client.send_message('/start')
    resp = responses_queue.get(timeout=10)
    assert resp.user_id == user_id
    assert resp.text == LINE_HELP_EN


def test_choose_language_cmd(serv_starter):
    user_id = USER_ID_3
    client = Client(USERNAME_3, user_id)

    client.send_message('/help')
    resp = responses_queue.get(timeout=10)
    assert resp.user_id == user_id
    assert resp.text == LINE_HELP_EN

    client.send_message('/change_language')
    resp = responses_queue.get(timeout=10)
    assert resp.user_id == user_id
    resp = responses_queue.get(timeout=10)
    assert resp.user_id == user_id

    client.send_message('/change_language__ru')
    resp = responses_queue.get(timeout=10)
    assert resp.user_id == user_id
    assert resp.text == "Язык сменен"
    resp = responses_queue.get(timeout=10)
    assert resp.user_id == user_id
    assert resp.text == LINE_HELP_RU


def test_create_team(serv_starter):
    create_team(
        username=USERNAME_4,
        user_id=USER_ID_4,
        team_name="konoha"
    )


def test_invite_to_team(serv_starter):
    invite_to_team(
        username=USERNAME_6,
        user_id=USER_ID_6,
        team_name="river",
        invited_username=USERNAME_7,
        invited_user_id=USER_ID_7
    )


def test_accept_team_invite(serv_starter):
    accept_team_invite(
        username=USERNAME_8,
        user_id=USER_ID_8,
        team_name="koshka",
        invited_username=USERNAME_9,
        invited_user_id=USER_ID_9
    )


def test_reject_team_invite(serv_starter):
    reject_team_invite(
        username=USERNAME_10,
        user_id=USER_ID_10,
        team_name="hikari",
        invited_username=USERNAME_11,
        invited_user_id=USER_ID_11
    )


def test_create_meeting(serv_starter):
    create_meeting(
        username=USERNAME_5,
        user_id=USER_ID_5,
        team_name="garden",
        meeting_desc="breakfast",
        meeting_time_str="11-11-2022 11:11"
    )
