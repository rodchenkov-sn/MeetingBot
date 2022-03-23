import pytest

from teams import Team, TeamsRepo, team_from_mongo, TeamPolicy

from test_mock_collection import MockCollection
from test_operators import team_eq_ignore_id


DEFAULT_TEAM_OWNER = 1
DEFAULT_TEAM_NAME = 'team'


def make_default_empty_team() -> Team:
    return Team(DEFAULT_TEAM_OWNER, DEFAULT_TEAM_NAME)


def make_default_policy() -> TeamPolicy:
    return TeamPolicy()


@pytest.fixture()
def resource_setup(request):
    collection = MockCollection()
    return (TeamsRepo(collection), collection)


def test_team_serialization(resource_setup):
    t = make_default_empty_team()
    s = t.serialize()
    assert team_from_mongo(s) == t

def test_add_team(resource_setup):
    repo, collection = resource_setup
    repo.add_team(make_default_empty_team())
    assert len(collection.items) == 1
    t = team_from_mongo(collection.items[0])
    assert t != make_default_empty_team()
    assert team_eq_ignore_id(t, make_default_empty_team())


def test_set_team_parent(resource_setup):
    repo, collection = resource_setup
    child_id = repo.add_team(make_default_empty_team())
    parent_id = repo.add_team(make_default_empty_team())
    repo.add_parent(child_id, parent_id)
    child_team = team_from_mongo(collection.items[0])
    parent_team = team_from_mongo(collection.items[1])
    assert child_team.parent == parent_id
    assert parent_team.children == [child_id]

def test_policy_propagation(resource_setup):
    repo, collection = resource_setup
    child_id = repo.add_team(make_default_empty_team())
    parent_id = repo.add_team(make_default_empty_team())
    repo.add_parent(child_id, parent_id)
    assert team_from_mongo(collection.items[0]).policy == TeamPolicy()
    propagated_policy = TeamPolicy()
    propagated_policy.propagate_policy = True
    propagated_policy.allow_users_to_create_meetings = not propagated_policy.allow_users_to_create_meetings
    repo.set_team_policy(parent_id, propagated_policy)
    child_team = repo.get_team(child_id)
    parent_team = repo.get_team(parent_id)
    assert parent_team.policy == propagated_policy
    assert child_team.policy == propagated_policy

def test_admin_propagation(resource_setup):
    repo, collection = resource_setup
    child_team = Team(1, 'child')
    parent_team = Team(2, 'parent')
    parent_team.policy.propagate_admin = False
    child_id = repo.add_team(child_team)
    parent_id = repo.add_team(parent_team)
    repo.add_parent(child_id, parent_id)
    assert list(repo.get_admins(child_id)) == [1]
    new_policy = parent_team.policy
    new_policy.propagate_admin = True
    repo.set_team_policy(parent_id, new_policy)
    new_admins = list(repo.get_admins(child_id))
    assert 1 in new_admins and 2 in new_admins and len(new_admins) == 2
