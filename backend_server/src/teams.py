import yaml

from typing import Iterable

from team_policy import TeamPolicy

from icollection import ICollection


class Team:
    def __init__(self, _owner: int, _name: str) -> None:
        self.id = -1
        self.owner = _owner
        self.name = _name
        self.members = [_owner]
        self.parent = -1
        self.children = []
        self.policy = TeamPolicy()
        self.uploaded_files = []

    def __eq__(self, other):
        return (
            self.id == other.id
            and self.owner == other.owner
            and self.members == other.members
            and self.parent == other.parent
            and self.children == other.children
            and self.policy == other.policy
        )

    def add_member(self, _member_id: int) -> None:
        self.members.append(_member_id)

    def serialize(self):
        return {
            '_id': self.id,
            'owner': self.owner,
            'name': self.name,
            'members': self.members,
            'parent': self.parent,
            'children': self.children,
            'allow_users_to_create_meetings': self.policy.allow_users_to_create_meetings,
            'need_approve_for_meeting_creation': self.policy.need_approve_for_meeting_creation,
            'propagate_policy': self.policy.propagate_policy,
            'parent_visible': self.policy.parent_visible,
            'propagate_admin': self.policy.propagate_admin,
            'uploaded_files': self.uploaded_files
        }


def team_from_mongo(item) -> Team:
    team = Team(item['owner'], item['name'])
    team.id = item['_id']
    team.members = item['members']
    team.parent = item['parent']
    team.children = item['children']
    team.uploaded_files = item['uploaded_files']
    policy = TeamPolicy()
    policy.need_approve_for_meeting_creation = item['need_approve_for_meeting_creation']
    policy.allow_users_to_create_meetings = item['allow_users_to_create_meetings']
    policy.propagate_policy = item['propagate_policy']
    policy.parent_visible = item['parent_visible']
    policy.propagate_admin = item['propagate_admin']
    team.policy = policy
    return team


class TeamsRepo:
    def __init__(self, collection: ICollection) -> None:
        self.__collection = collection

    def add_team(self, team: Team) -> int:
        from random import randint
        team.id = randint(0, int(9e10))
        self.__collection.insert_one(team.serialize())
        return team.id

    def get_teams_by_owner(self, _owner: int) -> Iterable[Team]:
        visited = set()
        to_visit = []
        for item in self.__collection.find_one({'owner': _owner}):
            to_visit.append(team_from_mongo(item))
        while to_visit:
            curr = to_visit.pop()
            if curr in visited:
                continue
            visited.add(curr)
            yield curr
            if curr.policy.propagate_admin:
                for child in curr.children:
                    to_visit.append(self.get_team(child))

    def get_team(self, _id: int) -> Team:
        return team_from_mongo(self.__collection.find_one({'_id': _id}))

    def add_member_to_team(self, _team_id: int, _member_id: int):
        self.__collection.push_to_one(_team_id, 'members', _member_id)

    def set_team_policy(self, _id: int, policy: TeamPolicy):
        self.__collection.set_one(_id, 'need_approve_for_meeting_creation', policy.need_approve_for_meeting_creation)
        self.__collection.set_one(_id, 'allow_users_to_create_meetings', policy.allow_users_to_create_meetings)
        self.__collection.set_one(_id, 'propagate_policy', policy.propagate_policy)
        self.__collection.set_one(_id, 'parent_visible', policy.parent_visible)
        self.__collection.set_one(_id, 'propagate_admin', policy.propagate_admin)
        if policy.propagate_policy:
            team = self.get_team(_id)
            for child in team.children:
                self.set_team_policy(child, policy)

    def get_grups_by_member(self, _user_id: int) -> Iterable[Team]:
        for item in self.__collection.find_many({'members': _user_id}):
            yield team_from_mongo(item)

    def add_parent(self, _group_id: int, _parent_id: int):
        self.__collection.set_one( _group_id, 'parent', _parent_id)
        self.__collection.push_to_one(_parent_id, 'children', _group_id)
        parent_team = self.get_team(_parent_id)
        child_team = self.get_team(_group_id)
        if parent_team.policy.propagate_policy:
            new_policy = parent_team.policy
            new_policy.propagate_policy = child_team.policy.propagate_policy
            self.set_team_policy(_group_id, new_policy)

    def get_invitable_members(self, _group_id: int) -> Iterable[int]:
        curr_team = self.get_team(_group_id)
        while curr_team.parent != -1 and self.get_team(curr_team.parent).policy.parent_visible:
            curr_team = self.get_team(curr_team.parent)
        visible_members = set()
        visited_teams = set()
        teams_to_visit = [curr_team.id]
        while len(teams_to_visit) != 0:
            curr = teams_to_visit.pop()
            if curr in visited_teams:
                continue
            visited_teams.add(curr)
            team = self.get_team(curr)
            visible_members.update(team.members)
            teams_to_visit += team.children
        for member in visible_members:
            yield member

    def get_admins(self, _group_id: int) -> Iterable[int]:
        curr_team_id = _group_id
        while curr_team_id != -1:
            curr_team = self.get_team(curr_team_id)
            if curr_team_id == _group_id or curr_team.policy.propagate_admin:
                yield curr_team.owner
                curr_team_id = curr_team.parent
            else:
                curr_team_id = -1

    def add_file_to_team(self, _team_id: int, _file_id: int):
        self.__collection.push_to_one(_team_id, 'uploaded_files', _file_id)

    def get_available_files(self, _team_id: int) -> Iterable[int]:
        curr_team = self.get_team(_team_id)
        while curr_team.parent != -1 and self.get_team(curr_team.parent).policy.parent_visible:
            curr_team = self.get_team(curr_team.parent)
        visible_files = set()
        visited_teams = set()
        teams_to_visit = [curr_team.id]
        while len(teams_to_visit) != 0:
            curr = teams_to_visit.pop()
            if curr in visited_teams:
                continue
            visited_teams.add(curr)
            team = self.get_team(curr)
            visible_files.update(team.uploaded_files)
            teams_to_visit += team.children
        for fid in visible_files:
            yield fid

    def get_teams_by_user(self, _user_id: int) -> Iterable[Team]:
        for item in self.__collection.find_many({'members': _user_id}):
            yield team_from_mongo(item)
