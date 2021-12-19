import grpc

from typing import Iterable
from concurrent import futures

import backend_service_pb2 as bs
import backend_service_pb2_grpc as bsg


class Team:
    def __init__(self, _owner: int, _name: str) -> None:
        self.owner = _owner
        self.name = _name
        self.members = [_owner]
    
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


teamsRepo = TeamsRepo()


class Meeting:
    def __init__(self, _creator: int, _team: int):
        self.id = -1
        self.creator = _creator
        self.team = _team
        self.desc = ''
        self.time = 0
        self.participants = [_creator]

    def set_id(self, _id: int) -> None:
        self.id = _id

    def add_participant(self, _participant: int) -> None:
        self.participants.append(_participant)

    def to_proto(self) -> bs.MeetingInfo:
        return bs.MeetingInfo(
            id=self.id,
            creator=self.creator,
            team=self.team,
            desc=self.desc,
            time=self.time
        )


def meeting_from_msg(info: bs.MeetingInfo) -> Meeting:
    meeting = Meeting(info.creator, info.team)
    meeting.id = info.id
    meeting.desc = info.desc
    meeting.time = info.time
    return meeting


class MeetingsRepo:
    def __init__(self):
        self.__meetings = []

    def add_meeting(self, meeting: Meeting):
        meeting.set_id(len(self.__meetings))
        self.__meetings.append(meeting)
        return meeting.id

    def update_meeting(self, meeting: Meeting):
        self.__meetings[meeting.id].desc = meeting.desc
        self.__meetings[meeting.id].time = meeting.time

    def get_meetings_by_owner(self, owner: int) -> Iterable[Meeting]:
        for meeting in self.__meetings:
            if meeting.creator == owner:
                yield meeting

    def add_participant(self, meeting_id: int, user_id: int):
        self.__meetings[meeting_id].add_participant(user_id)

    def get_meeting(self, meeting_id: int) -> Meeting:
        return self.__meetings[meeting_id]


meetingsRepo = MeetingsRepo()


class BackendServiceHandler(bsg.BackendServiceServicer):
    def CreateTeam(self, request, context):
        team_id = teamsRepo.add_team(Team(request.owner, request.name))
        return bs.EntityId(id=team_id)

    def GetOwnedTeams(self, request, context):
        for team in teamsRepo.get_teams_by_owner(request.id):
            yield bs.NamedInfo(id=team.id, name=team.name)

    def GetTeamInfo(self, request, context):
        team = teamsRepo.get_team(request.id)
        return bs.NamedInfo(id=team.id, name=team.name)

    def AddTeamMember(self, request, context):
        teamsRepo.add_member_to_team(request.object, request.subject)
        return bs.SimpleResponse(ok=True)

    def CreateMeeting(self, request, context):
        meeting_id = meetingsRepo.add_meeting(Meeting(request.creator, request.team))
        return bs.EntityId(id=meeting_id)

    def UpdateMeetingInfo(self, request, context):
        meetingsRepo.update_meeting(meeting_from_msg(request))
        return bs.SimpleResponse(ok=True)

    def GetOwnedMeetings(self, request, context):
        for meeting in meetingsRepo.get_meetings_by_owner(request.id):
            yield bs.NamedInfo(id=meeting.id, name=meeting.desc)

    def AddParticipant(self, request, context):
        meetingsRepo.add_participant(request.object, request.subject)
        return bs.SimpleResponse(ok=True)

    def GetMeetingInfo(self, request, context):
        return meetingsRepo.get_meeting(request.id).to_proto()


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    bsg.add_BackendServiceServicer_to_server(BackendServiceHandler(), server)
    server.add_insecure_port('[::]:50052')
    server.start()
    server.wait_for_termination()
