import random
import grpc
import yaml

from concurrent import futures
from typing import Any

import backend_service_pb2 as bs
import backend_service_pb2_grpc as bsg

from team_policy import TeamPolicy, policy_from_msg
from teams import Team, TeamsRepo
from meetings import Meeting, MeetingsRepo, meeting_from_msg
from mongo_collection import MongoCollection

import calendar_service_pb2 as cs
import calendar_service_pb2_grpc as css


class BackendServiceHandler(bsg.BackendServiceServicer):
    def __init__(self, teams_repo: TeamsRepo, meetings_repo: MeetingsRepo, calendar_service: Any):
        super().__init__()
        self.__teams_repo = teams_repo
        self.__meetings_repo = meetings_repo
        self.__calendar_service = calendar_service

    def CreateTeam(self, request, context):
        team_id = self.__teams_repo.add_team(Team(request.owner, request.name))
        return bs.EntityId(id=team_id)

    def GetOwnedTeams(self, request, context):
        for team in self.__teams_repo.get_teams_by_owner(request.id):
            yield bs.NamedInfo(id=team.id, name=team.name)

    def GetTeamInfo(self, request, context):
        team = self.__teams_repo.get_team(request.id)
        return bs.NamedInfo(id=team.id, name=team.name)

    def AddTeamMember(self, request, context):
        self.__teams_repo.add_member_to_team(request.object, request.subject)
        return bs.SimpleResponse(ok=True)

    def CreateMeeting(self, request, context):
        meeting_id = self.__meetings_repo.add_meeting(Meeting(request.creator, request.team))
        return bs.EntityId(id=meeting_id)

    def UpdateMeetingInfo(self, request, context):
        self.__meetings_repo.update_meeting(meeting_from_msg(request))
        m = self.__meetings_repo.get_meeting(request.id)
        if m.time > 0 and m.desc != '':
            for uid in set(m.participants):
                self.__calendar_service.PushEvent(cs.CalendarEvent(
                    user_id=uid,
                    meeting_id=m.id,
                    desc=m.desc,
                    time=m.time
                ))
        return bs.SimpleResponse(ok=True)

    def GetOwnedMeetings(self, request, context):
        for meeting in self.__meetings_repo.get_meetings_by_owner(request.id):
            if meeting.approved:
                yield bs.NamedInfo(id=meeting.id, name=meeting.desc)

    def AddParticipant(self, request, context):
        self.__meetings_repo.add_participant(request.object, request.subject)
        m = self.__meetings_repo.get_meeting(request.object)
        for uid in set(m.participants):
            self.__calendar_service.PushEvent(cs.CalendarEvent(
                user_id=uid,
                meeting_id=m.id,
                desc=m.desc,
                time=m.time
            ))
        return bs.SimpleResponse(ok=True)

    def GetMeetingInfo(self, request, context):
        return self.__meetings_repo.get_meeting(request.id).to_proto()

    def GetTeamMembers(self, request, context):
        for member in self.__teams_repo.get_team(request.id).members:
            yield bs.EntityId(id=member)

    def ApproveMeeting(self, request, context):
        self.__meetings_repo.approve_meeting(request.id)
        m = self.__meetings_repo.get_meeting(request.id)
        for uid in set(m.participants):
            self.__calendar_service.PushEvent(cs.CalendarEvent(
                user_id=uid,
                meeting_id=m.id,
                desc=m.desc,
                time=m.time
            ))
        return bs.SimpleResponse(ok=True)

    def GetGroupMeetings(self, request, context):
        for meeting in self.__meetings_repo.get_meetings_by_group(request.id):
            yield bs.NamedInfo(id=meeting.id, name=meeting.desc)
    
    def GetGroupOwner(self, request, context):
        return bs.EntityId(id=self.__teams_repo.get_team(request.id).owner)

    def GetGroupPolicy(self, request, context):
        policy = self.__teams_repo.get_team(request.id).policy
        return bs.TeamPolicy(
            groupId=request.id, 
            allowUsersToCreateMeetings=policy.allow_users_to_create_meetings, 
            needApproveForMeetingCreation=policy.need_approve_for_meeting_creation,
            propagatePolicy=policy.propagate_policy,
            parentVisible=policy.parent_visible,
            propagateAdmin=policy.propagate_admin
        )

    def SetGroupPolicy(self, request, context):
        self.__teams_repo.set_team_policy(request.groupId, policy_from_msg(request))
        return bs.SimpleResponse(ok=True)

    def GetGroupsToCreateMeeting(self, request, context):
        for team in self.__teams_repo.get_grups_by_member(request.id):
            if team.owner == request.id or team.policy.allow_users_to_create_meetings:
                yield bs.NamedInfo(id=team.id, name=team.name)

    def AddParentTeam(self, request, context):
        self.__teams_repo.add_parent(request.subject, request.object)
        return bs.SimpleResponse(ok=True)

    def GetInvitableMembers(self, request, context):
        for member in self.__teams_repo.get_invitable_members(request.id):
            yield bs.EntityId(id=member)

    def GetGroupOwners(self, request, context):
        for admin in self.__teams_repo.get_admins(request.id):
            yield bs.EntityId(id=admin)

    def GetUserMeetings(self, request, context):
        uid = request.id
        for meeting in self.__meetings_repo.get_meetings_my_user(uid):
            yield bs.NamedInfo(id=meeting.id, name=meeting.desc)

    def GetMeetingMembers(self, request, context):
        mid = request.id
        meeting = self.__meetings_repo.get_meeting(mid)
        for uid in set(meeting.participants):
            yield bs.EntityId(id=uid)

    def AddFileToTeam(self, request, context):
        print(request)
        self.__teams_repo.add_file_to_team(request.object, request.subject)
        return bs.SimpleResponse(ok=True)

    def GetAvailableFiles(self, request, context):
        for fid in self.__teams_repo.get_available_files(request.id):
            yield bs.EntityId(id=fid)

    def GetTeamsByUser(self, request, context):
        for team in self.__teams_repo.get_teams_by_user(request.id):
            yield bs.NamedInfo(id=team.id, name=team.name)


def serve():
    random.seed()
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))

    with open('config.yml', 'r') as config_file:
        config = yaml.safe_load(config_file)

    teams_repo = TeamsRepo(MongoCollection(config['teams_repo_url'], 'MeetingBotDB', 'Teams'))
    meetings_repo = MeetingsRepo(MongoCollection(config['meetings_repo_url'], 'MeetingBotDB', 'Meetings'))
    channel_calendar = grpc.insecure_channel('calendar-service:50053')
    calendar_stub = css.CalendarServiceStub(channel_calendar)

    bsg.add_BackendServiceServicer_to_server(BackendServiceHandler(teams_repo, meetings_repo, calendar_stub), server)
    server.add_insecure_port('[::]:50062')
    server.start()
    server.wait_for_termination()
