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


@pytest.fixture(scope='session', autouse=True)
def serv_starter():
    start_server()
    yield True
    stop_server()


def test_help_cmd(serv_starter):
    user_id = 1488
    client = Client('Ayanami', user_id)

    client.send_message('/help')
    resp = responses_queue.get(timeout=10)
    assert resp.user_id == user_id
    assert resp.text == LINE_HELP_EN


def test_start_cmd(serv_starter):
    user_id = 1523
    client = Client('Rudy', user_id)

    client.send_message('/start')
    resp = responses_queue.get(timeout=10)
    assert resp.user_id == user_id
    assert resp.text == LINE_HELP_EN


def test_choose_language_cmd(serv_starter):
    user_id = 9999
    client = Client('Asuna', user_id)

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
    user_id = 6969
    team_name = "konoha"
    client = Client('Sakura', user_id)

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


def test_create_meeting(serv_starter):
    user_id = 7777
    team_name = "garden"
    pattern_team_id = re.compile(rf"/create_meeting[0-9]+ -- {team_name}\n")
    meeting_desc = "breakfast"
    meeting_time_str = "11-11-2022 11:11"
    client = Client('Rosy', user_id)

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
