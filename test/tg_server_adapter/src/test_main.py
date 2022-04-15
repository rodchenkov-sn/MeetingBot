import pytest

import string
import random

import re

from server import start_server, stop_server, Client, responses_queue, messages_queue

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


def random_str(n):
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(n))


def stress():
    client = Client(random_str(8), random.randint(1, 99999))
    for _ in range(1000):
        client.send_message('/get_agenda_today')
    messages_queue.join()


@pytest.fixture(scope='session', autouse=True)
def serv_starter():
    start_server()
    yield True
    stress()
    stop_server()


def test_help_cmd(serv_starter):
    user_id = random.randint(1, 99999)
    username = random_str(8)
    client = Client(username, user_id)

    client.send_message('/help')
    resp = responses_queue.get(timeout=10)
    assert resp.user_id == user_id
    assert resp.text == LINE_HELP_EN


def test_start_cmd(serv_starter):
    user_id = random.randint(1, 99999)
    username = random_str(8)
    client = Client(username, user_id)

    client.send_message('/start')
    resp = responses_queue.get(timeout=10)
    assert resp.user_id == user_id
    assert resp.text == LINE_HELP_EN


def test_choose_language_cmd(serv_starter):
    user_id = random.randint(1, 99999)
    username = random_str(8)
    client = Client(username, user_id)

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


def test_stability_create(serv_starter):
    user_id = random.randint(1, 99999)
    username = random_str(8)
    client = Client(username, user_id)

    for x in range(1, 100):
        client.send_message('/create_team')
        responses_queue.get(timeout=10)
        team_name = random_str(10)
        client.send_message(team_name)
        resp = responses_queue.get(timeout=10)
        assert resp.text == f"{team_name} team created!"
        responses_queue.get(timeout=10)


def test_escaped_name(serv_starter):
    user_id = random.randint(1, 99999)
    username = random_str(8)
    client = Client(username, user_id)
    client.send_message('/create_team')
    responses_queue.get(timeout=10)
    team_name = "\n"
    client.send_message(team_name)
    resp = responses_queue.get(timeout=10)
    assert resp.text == f"{team_name} team created!"
    responses_queue.get(timeout=10)


def test_auth_gcal(serv_starter):
    user_id = random.randint(1, 99999)
    username = random_str(8)
    client = Client(username, user_id)
    client.send_message('/auth_gcal')
    responses_queue.get(timeout=10)
    client.send_message('123')
    res = responses_queue.get(timeout=10)
    assert res.text == 'Authenticated!'

    
def test_create_team(serv_starter):
    create_team(
        username=random_str(8),
        user_id=random.randint(1, 99999),
        team_name=random_str(8)
    )



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
    user_id = random.randint(1, 99999)
    username = random_str(8)
    client = Client(username, user_id)

    client.send_message('/help')
    resp = responses_queue.get(timeout=10)
    assert resp.user_id == user_id
    assert resp.text == LINE_HELP_EN


def test_start_cmd(serv_starter):
    user_id = random.randint(1, 99999)
    username = random_str(8)
    client = Client(username, user_id)

    client.send_message('/start')
    resp = responses_queue.get(timeout=10)
    assert resp.user_id == user_id
    assert resp.text == LINE_HELP_EN


def test_choose_language_cmd(serv_starter):
    user_id = random.randint(1, 99999)
    username = random_str(8)
    client = Client(username, user_id)

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
        username=random_str(8),
        user_id=random.randint(1, 99999),
        team_name=random_str(8)
    )


def test_invite_to_team(serv_starter):
    invite_to_team(
        username=random_str(8),
        user_id=random.randint(1, 99999),
        team_name=random_str(8),
        invited_username=random_str(8),
        invited_user_id=random.randint(1, 99999)
    )


def test_accept_team_invite(serv_starter):
    accept_team_invite(
        username=random_str(8),
        user_id=random.randint(1, 99999),
        team_name=random_str(8),
        invited_username=random_str(8),
        invited_user_id=random.randint(1, 99999)
    )


def test_reject_team_invite(serv_starter):
    reject_team_invite(
        username=random_str(8),
        user_id=random.randint(1, 99999),
        team_name="hikari",
        invited_username=random_str(8),
        invited_user_id=random.randint(1, 99999)
    )


def test_create_meeting(serv_starter):
    create_meeting(
        username=random_str(8),
        user_id=random.randint(1, 99999),
        team_name=random_str(8),
        meeting_desc=random_str(8),
        meeting_time_str="11-11-2022 11:11"
    )
