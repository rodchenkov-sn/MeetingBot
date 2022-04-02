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

def test_get_group_by_member_no_team(resource_setup):
    repo, collection = resource_setup
    teams = list(repo.get_grups_by_member(100))
    assert len(teams) == 0

def test_get_group_by_member_invalid_member(resource_setup):
    repo, collection = resource_setup
    team = make_default_empty_team()
    owner = team.owner
    team_id = repo.add_team(team)
    teams = list(repo.get_grups_by_member(owner + 1))
    assert len(teams) == 0

def test_get_groups_by_member(resource_setup):
    repo, collection = resource_setup
    repo, collection = resource_setup
    team = make_default_empty_team()
    owner = team.owner
    team_id = repo.add_team(team)
    teams = list(repo.get_grups_by_member(owner))
    assert len(teams) == 1
    t = teams[0]
    assert team_eq_ignore_id(t, team)

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

def test_add_parent_no_parent(resource_setup):
    repo, collection = resource_setup
    child_team = Team(1, 'child')
    child_id = repo.add_team(child_team)
    with pytest.raises(ValueError):
        repo.add_parent(child_id, child_id + 1)

def test_add_parent_no_child(resource_setup):
    repo, collection = resource_setup
    parent_team = Team(2, 'parent')
    parent_id = repo.add_team(parent_team)
    with pytest.raises(ValueError):
        repo.add_parent(parent_id + 1, parent_id)

def test_add_parent_both_invalid(resource_setup):
    repo, collection = resource_setup
    with pytest.raises(ValueError):
        repo.add_parent(1, 2)

def test_set_policy_no_team(resource_setup):
    repo, collection = resource_setup
    policy = TeamPolicy()
    with pytest.raises(ValueError):
        repo.set_team_policy(100, policy)

def test_add_member_no_team(resource_setup):
    repo, collection = resource_setup
    with pytest.raises(ValueError):
        repo.add_member_to_team(100, 101)

def test_default_team_member(resource_setup):
    repo, collection = resource_setup
    team = make_default_empty_team()
    team_id = repo.add_team(team)
    assert collection.items[0]['members'] == [team.owner]

def test_add_team_member(resource_setup):
    repo, collection = resource_setup
    team = make_default_empty_team()
    team_id = repo.add_team(team)
    member_id = team_id + 1
    repo.add_member_to_team(team_id, member_id)
    assert len(collection.items[0]['members']) == 2
    assert member_id in collection.items[0]['members']

def test_file_upload_no_team(resource_setup):
    repo, collection = resource_setup
    file_id = 3
    team_id = 1
    with pytest.raises(ValueError):
        repo.add_file_to_team(team_id, file_id)

def test_file_upload(resource_setup):
    repo, collection = resource_setup
    team = make_default_empty_team()
    team_id = repo.add_team(team)
    file_id = 3
    repo.add_file_to_team(team_id, file_id)
    assert len(collection.items[0]['uploaded_files']) == 1

def test_get_available_files(resource_setup):
    repo, collection = resource_setup
    team = make_default_empty_team()
    team_id = repo.add_team(team)
    file_id = 3
    repo.add_file_to_team(team_id, file_id)
    assert len(list(repo.get_available_files(team_id))) == 1

def test_get_teams_by_user(resource_setup):
    repo, collection = resource_setup
    team = make_default_empty_team()
    owner = team.owner
    team_id = repo.add_team(team)
    teams = list(repo.get_teams_by_user(owner))
    assert len(teams) == 1
    t = teams[0]
    assert team_eq_ignore_id(t, team)

def test_get_teams_by_user_no_teams(resource_setup):
    repo, collection = resource_setup
    teams = list(repo.get_teams_by_user(100))
    assert len(teams) == 0

def test_get_teams_by_user_invalid_user(resource_setup):
    repo, collection = resource_setup
    team = make_default_empty_team()
    owner = team.owner
    team_id = repo.add_team(team)
    teams = list(repo.get_teams_by_user(owner + 1))
    assert len(teams) == 0
