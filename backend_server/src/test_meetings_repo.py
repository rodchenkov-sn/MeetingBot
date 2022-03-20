import pytest

import startup # for correct coverage without __init__.py

from meetings import MeetingsRepo, Meeting, meeting_from_mongo
from test_mock_collection import MockCollection


def get_default_meeting_creator() -> int:
    return 1

def get_default_meeting_team() -> int:
    return 2

def get_default_meeting_desc() -> str:
    return 'desc'

def get_default_meeting_time() -> int:
    return 11

def make_default_test_meeting() -> Meeting:
    m = Meeting(get_default_meeting_creator(), get_default_meeting_team())
    m.desc = get_default_meeting_desc()
    m.time = get_default_meeting_time()
    return m

def make_default_empty_meeting() -> Meeting:
    return Meeting(get_default_meeting_creator(), get_default_meeting_team())

@pytest.fixture()
def resource_setup(request):
    collection = MockCollection()
    return (MeetingsRepo(collection), collection)

def test_meeting_serialization(resource_setup):
    m = make_default_test_meeting()
    s = m.serialize()
    assert m == meeting_from_mongo(s)

def test_add_meeting(resource_setup):
    repo, collection = resource_setup
    repo.add_meeting(make_default_test_meeting())
    assert len(collection.items) == 1
    assert collection.items[0]['creator'] == get_default_meeting_creator()
    assert collection.items[0]['team'] == get_default_meeting_team()

def test_add_meeting_ignore_initial_id(resource_setup):
    repo, collection = resource_setup
    m1 = make_default_test_meeting()
    m2 = make_default_test_meeting()
    m1.id = 1
    m2.id = 1
    repo.add_meeting(m1)
    repo.add_meeting(m2)
    assert len(collection.items) == 2
    assert collection.items[0]['_id'] != collection.items[1]['_id']

def test_update_meeting_full(resource_setup):
    repo, collection = resource_setup
    repo.add_meeting(make_default_test_meeting())
    id = collection.items[0]['_id']
    updated_meeting = make_default_test_meeting()
    updated_meeting.id = id
    updated_meeting.desc = get_default_meeting_desc()
    updated_meeting.time = get_default_meeting_time()
    repo.update_meeting(updated_meeting)
    assert len(collection.items) == 1
    item = collection.items[0]
    assert item['creator'] == get_default_meeting_creator()
    assert item['team'] == get_default_meeting_team()
    assert item['_id'] == id
    assert item['desc'] == get_default_meeting_desc()
    assert item['time'] == get_default_meeting_time()

def test_update_non_existing_meeting(resource_setup):
    repo, collection = resource_setup
    repo.add_meeting(make_default_test_meeting())
    updated_meeting = make_default_test_meeting()
    updated_meeting.id = -1
    updated_meeting.desc = get_default_meeting_desc()
    updated_meeting.time = get_default_meeting_time()
    with pytest.raises(ValueError):
        repo.update_meeting(updated_meeting)

def test_update_meeting_empty_desc(resource_setup):
    repo, collection = resource_setup
    repo.add_meeting(make_default_empty_meeting())
    id = collection.items[0]['_id']
    updated_meeting = make_default_empty_meeting()
    updated_meeting.id = id
    updated_meeting.desc = ''
    updated_meeting.time = get_default_meeting_time()
    repo.update_meeting(updated_meeting)
    assert len(collection.items) == 1
    item = collection.items[0]
    assert item['creator'] == get_default_meeting_creator()
    assert item['team'] == get_default_meeting_team()
    assert item['_id'] == id
    assert item['desc'] == ''
    assert item['time'] == get_default_meeting_time()

def test_update_meeting_none_desc(resource_setup):
    repo, collection = resource_setup
    repo.add_meeting(make_default_empty_meeting())
    id = collection.items[0]['_id']
    updated_meeting = make_default_empty_meeting()
    updated_meeting.id = id
    updated_meeting.desc = None
    updated_meeting.time = get_default_meeting_time()
    repo.update_meeting(updated_meeting)
    assert len(collection.items) == 1
    item = collection.items[0]
    assert item['creator'] == get_default_meeting_creator()
    assert item['team'] == get_default_meeting_team()
    assert item['_id'] == id
    assert item['desc'] == ''
    assert item['time'] == get_default_meeting_time()

def test_update_meeting_negative_time(resource_setup):
    repo, collection = resource_setup
    repo.add_meeting(make_default_empty_meeting())
    id = collection.items[0]['_id']
    updated_meeting = make_default_empty_meeting()
    updated_meeting.id = id
    updated_meeting.desc = get_default_meeting_desc()
    updated_meeting.time = -1
    repo.update_meeting(updated_meeting)
    assert len(collection.items) == 1
    item = collection.items[0]
    assert item['creator'] == get_default_meeting_creator()
    assert item['team'] == get_default_meeting_team()
    assert item['_id'] == id
    assert item['desc'] == get_default_meeting_desc()
    assert item['time'] == 0

def test_update_meeting_none_time(resource_setup):
    repo, collection = resource_setup
    repo.add_meeting(make_default_empty_meeting())
    id = collection.items[0]['_id']
    updated_meeting = make_default_empty_meeting()
    updated_meeting.id = id
    updated_meeting.desc = get_default_meeting_desc()
    updated_meeting.time = None
    repo.update_meeting(updated_meeting)
    assert len(collection.items) == 1
    item = collection.items[0]
    assert item['creator'] == get_default_meeting_creator()
    assert item['team'] == get_default_meeting_team()
    assert item['_id'] == id
    assert item['desc'] == get_default_meeting_desc()
    assert item['time'] == 0

def test_get_meetings_by_owner_empty_repo(resource_setup):
    repo, collection = resource_setup
    meetings = list(repo.get_meetings_by_owner(get_default_meeting_creator()))
    assert len(meetings) == 0

def test_get_meetings_by_owner_no_result(resource_setup):
    repo, collection = resource_setup
    repo.add_meeting(make_default_test_meeting())
    ms = list(repo.get_meetings_by_owner(get_default_meeting_creator() + 1))
    assert len(ms) == 0

def test_get_meetings_by_owner_no_approval(resource_setup):
    repo, collection = resource_setup
    repo.add_meeting(make_default_empty_meeting())
    ms = list(repo.get_meetings_by_owner(get_default_meeting_creator()))
    assert len(ms) == 0

def test_get_meetings_by_owner_approved(resource_setup):
    repo, collection = resource_setup
    m = make_default_empty_meeting()
    m.approved = True
    repo.add_meeting(m)
    ms = list(repo.get_meetings_by_owner(get_default_meeting_creator()))
    assert len(ms) == 1

def test_have_creator_as_participant(resource_setup):
    repo, collection = resource_setup
    repo.add_meeting(make_default_empty_meeting())
    i = collection.items[0]
    assert len(i['participants']) == 1
    assert get_default_meeting_creator() in i['participants']

def test_add_participants(resource_setup):
    repo, collection = resource_setup
    repo.add_meeting(make_default_empty_meeting())
    id = collection.items[0]['_id']
    p = get_default_meeting_creator() + 1
    repo.add_participant(id, p)
    i = collection.items[0]
    assert len(i['participants']) == 2
    assert p in i['participants']

def test_approve_meeting(resource_setup):
    repo, collection = resource_setup
    repo.add_meeting(make_default_empty_meeting())
    id = collection.items[0]['_id']
    i = collection.items[0]
    assert not i['approved']
    repo.approve_meeting(id)
    assert i['approved']

def test_get_meetings_by_user_empty(resource_setup):
    repo, collection = resource_setup
    ms = list(repo.get_meetings_my_user(get_default_meeting_creator()))
    assert len(ms) == 0

def test_get_meetings_by_user_no_approve(resource_setup):
    repo, collection = resource_setup
    repo.add_meeting(make_default_empty_meeting())
    ms = list(repo.get_meetings_my_user(get_default_meeting_creator()))
    assert len(ms) == 0

def test_get_meetings_by_user_approved(resource_setup):
    repo, collection = resource_setup
    m = make_default_empty_meeting()
    m.approved = True
    repo.add_meeting(m)
    ms = list(repo.get_meetings_my_user(get_default_meeting_creator()))
    assert len(ms) == 1


