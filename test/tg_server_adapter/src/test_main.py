import pytest

from server import start_server, stop_server, Client, responses_queue


@pytest.fixture(scope='session', autouse=True)
def serv_starter():
    start_server()
    yield True
    stop_server()


def test_test(serv_starter):
    client = Client('Ayanami', 1488)
    client.send_message('hi')
    resp = responses_queue.get(timeout=10)
    assert resp.text != 'hi'
