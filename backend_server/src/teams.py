from typing import Iterable

from team_policy import TeamPolicy


class Team:
    def __init__(self, _owner: int, _name: str) -> None:
        self.owner = _owner
        self.name = _name
        self.members = [_owner]
        self.policy = TeamPolicy()
    
    def set_id(self, _id: int) -> None:
        self.id = _id

    def add_member(self, _member_id: int) -> None:
        self.members.append(_member_id)


class TeamsRepo:
    def __init__(self) -> None:
        self.__teams = []

    def add_team(self, team: Team) -> int:
        team.set_id(len(self.__teams))
        self.__teams.append(team)
        return team.id

    def get_teams_by_owner(self, _owner: int) -> Iterable[Team]:
        for team in self.__teams:
            if team.owner == _owner:
                yield team

    def get_team(self, _id: int) -> Team:
        return self.__teams[_id]

    def add_member_to_team(self, _team_id: int, _member_id: int) -> None:
        self.__teams[_team_id].add_member(_member_id)

    def get_team_members(self, _id: int) -> Iterable[int]:
        for member in self.__teams[_id].members:
            yield member

    def set_team_policy(self, _id: int, policy: TeamPolicy):
        self.__teams[_id].policy = policy
