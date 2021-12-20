from typing import Iterable

from team_policy import TeamPolicy


class Team:
    def __init__(self, _owner: int, _name: str) -> None:
        self.id = -1
        self.owner = _owner
        self.name = _name
        self.members = [_owner]
        self.policy = TeamPolicy()

    def add_member(self, _member_id: int) -> None:
        self.members.append(_member_id)

    def serialize(self):
        return {
            '_id': self.id,
            'owner': self.owner,
            'name': self.name,
            'members': self.members,
            'allow_users_to_create_meetings': self.policy.allow_users_to_create_meetings,
            'need_approve_for_meeting_creation': self.policy.need_approve_for_meeting_creation
        }


def team_from_mongo(item) -> Team:
    team = Team(item['owner'], item['name'])
    team.id = item['_id']
    team.members = item['members']
    policy = TeamPolicy()
    policy.need_approve_for_meeting_creation = item['need_approve_for_meeting_creation']
    policy.allow_users_to_create_meetings = item['allow_users_to_create_meetings']
    team.policy = policy
    return team


class TeamsRepo:
    def __init__(self) -> None:
        from pymongo import MongoClient
        client = MongoClient('')
        self.__collection = client['MeetingBotDB']['Teams']

    def add_team(self, team: Team) -> int:
        from random import randint
        team.id = randint(0, 9e10)
        self.__collection.insert_one(team.serialize())
        return team.id

    def get_teams_by_owner(self, _owner: int) -> Iterable[Team]:
        for item in self.__collection.find({'owner': _owner}):
            yield team_from_mongo(item)

    def get_team(self, _id: int) -> Team:
        return team_from_mongo(self.__collection.find_one({'_id': _id}))

    def add_member_to_team(self, _team_id: int, _member_id: int):
        self.__collection.update_one({'_id': _team_id}, {'$push': {'members': _member_id}})

    def set_team_policy(self, _id: int, policy: TeamPolicy):
        self.__collection.update_one({'_id': _id}, {'$set': {'need_approve_for_meeting_creation': policy.need_approve_for_meeting_creation}})
        self.__collection.update_one({'_id': _id}, {'$set': {'allow_users_to_create_meetings': policy.allow_users_to_create_meetings}})

    def get_grups_by_member(self, _user_id: int) -> Iterable[Team]:
        for item in self.__collection.find({'members': _user_id}):
            yield team_from_mongo(item)
