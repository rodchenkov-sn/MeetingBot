import pytest
from meetings import MeetingsRepo
from teams import TeamsRepo

from backend_service import BackendServiceHandler
from teams import Team
from meetings import Meeting
from test_mock_collection import MockCollection
from test_operators import team_eq_ignore_id, meeting_eq_ignore_id

import backend_service_pb2 as bs


class CalendarServiceStub:
    def __init__(self):
        self.timesPushed = 0

    def PushEvent(self, event):
        self.timesPushed += 1


class ResourceSetup:
    def __init__(self, service: BackendServiceHandler, teams: TeamsRepo, meetings: MeetingsRepo, calendar: CalendarServiceStub):
        self.service = service
        self.teams = teams
        self.meetings = meetings
        self.calendar = calendar


@pytest.fixture()
def resource_setup():
    tr = TeamsRepo(MockCollection())
    mr = MeetingsRepo(MockCollection())
    c = CalendarServiceStub()
    s = BackendServiceHandler(tr, mr, c)
    return ResourceSetup(s, tr, mr, c)

def test_create_team(resource_setup: ResourceSetup):
    team = Team(1, 'team')
    msg = bs.CreateTeamMsg(name=team.name, owner=team.owner)
    team_id = resource_setup.service.CreateTeam(msg, None).id
    created_team = resource_setup.teams.get_team(team_id)
    assert team_eq_ignore_id(team, created_team)

def test_create_meeting(resource_setup: ResourceSetup):
    meeting = Meeting(1, 1)
    msg = bs.MeetingInfo(
        id=-1,
        creator=meeting.creator,
        team=meeting.team,
        desc=meeting.desc,
        time=meeting.time
    )
    meeting_id = resource_setup.service.CreateMeeting(msg, None).id
    created_meeting = resource_setup.meetings.get_meeting(meeting_id)
    assert meeting_eq_ignore_id(created_meeting, meeting)

def test_create_meeting_ignore_id(resource_setup: ResourceSetup):
    meeting = Meeting(1, 1)
    msg1 = bs.MeetingInfo(
        id=-1,
        creator=meeting.creator,
        team=meeting.team,
        desc=meeting.desc,
        time=meeting.time
    )
    meeting_id1 = resource_setup.service.CreateMeeting(msg1, None).id
    created_meeting1 = resource_setup.meetings.get_meeting(meeting_id1)
    assert meeting_eq_ignore_id(created_meeting1, meeting)
    msg2 = bs.MeetingInfo(
        id=100,
        creator=meeting.creator,
        team=meeting.team,
        desc=meeting.desc,
        time=meeting.time
    )
    meeting_id2 = resource_setup.service.CreateMeeting(msg2, None).id
    created_meeting2 = resource_setup.meetings.get_meeting(meeting_id2)
    assert meeting_eq_ignore_id(created_meeting2, meeting)

def test_get_groups_to_create_meeting_on_policy(resource_setup: ResourceSetup):
    pt_adm = 1
    ct_adm = 2
    pt = Team(pt_adm, 'parent')
    ct = Team(ct_adm, 'child')
    add_pc_msg = bs.CreateTeamMsg(
        name=pt.name,
        owner=pt.owner
    )
    pt_id = resource_setup.service.CreateTeam(add_pc_msg, None).id
    add_ct_msg = bs.CreateTeamMsg(
        name=ct.name,
        owner=ct.owner
    )
    ct_id = resource_setup.service.CreateTeam(add_ct_msg, None).id
    teams_parent_adm = list(resource_setup.service.GetGroupsToCreateMeeting(
        bs.EntityId(id=pt_adm), None
    ))
    assert len(teams_parent_adm) == 1
    teams_child_adm = list(resource_setup.service.GetGroupsToCreateMeeting(
        bs.EntityId(id=ct_adm), None
    ))
    assert len(teams_child_adm) == 1
    assert resource_setup.service.AddParentTeam(
        bs.Participating(object=pt_id, subject=ct_id), None
    ).ok
    teams_parent_adm = list(resource_setup.service.GetGroupsToCreateMeeting(
        bs.EntityId(id=pt_adm), None
    ))
    assert len(teams_parent_adm) == 1
    teams_child_adm = list(resource_setup.service.GetGroupsToCreateMeeting(
        bs.EntityId(id=ct_adm), None
    ))
    assert len(teams_child_adm) == 1
    propagation_policy_msg = bs.TeamPolicy(
        groupId=pt_id,
        allowUsersToCreateMeetings=True,
        needApproveForMeetingCreation=False,
        propagatePolicy=True,
        parentVisible=True,
        propagateAdmin=True
    )
    assert resource_setup.service.SetGroupPolicy(propagation_policy_msg, None).ok
    teams_parent_adm = list(resource_setup.service.GetGroupsToCreateMeeting(
        bs.EntityId(id=pt_adm), None
    ))
    assert len(teams_parent_adm) == 1
    teams_child_adm = list(resource_setup.service.GetGroupsToCreateMeeting(
        bs.EntityId(id=ct_adm), None
    ))
    assert len(teams_child_adm) == 1

def test_get_owned_groups_on_policy(resource_setup: ResourceSetup):
    pt_adm = 1
    ct_adm = 2
    pt = Team(pt_adm, 'parent')
    ct = Team(ct_adm, 'child')
    add_pc_msg = bs.CreateTeamMsg(
        name=pt.name,
        owner=pt.owner
    )
    pt_id = resource_setup.service.CreateTeam(add_pc_msg, None).id
    add_ct_msg = bs.CreateTeamMsg(
        name=ct.name,
        owner=ct.owner
    )
    ct_id = resource_setup.service.CreateTeam(add_ct_msg, None).id
    teams_parent_adm = list(resource_setup.service.GetOwnedTeams(
        bs.EntityId(id=pt_adm), None
    ))
    assert len(teams_parent_adm) == 1
    teams_child_adm = list(resource_setup.service.GetOwnedTeams(
        bs.EntityId(id=ct_adm), None
    ))
    assert len(teams_child_adm) == 1
    assert resource_setup.service.AddParentTeam(
        bs.Participating(object=pt_id, subject=ct_id), None
    ).ok
    teams_parent_adm = list(resource_setup.service.GetOwnedTeams(
        bs.EntityId(id=pt_adm), None
    ))
    assert len(teams_parent_adm) == 2
    teams_child_adm = list(resource_setup.service.GetOwnedTeams(
        bs.EntityId(id=ct_adm), None
    ))
    assert len(teams_child_adm) == 1
    propagation_policy_msg = bs.TeamPolicy(
        groupId=pt_id,
        allowUsersToCreateMeetings=True,
        needApproveForMeetingCreation=False,
        propagatePolicy=True,
        parentVisible=False,
        propagateAdmin=False
    )
    assert resource_setup.service.SetGroupPolicy(propagation_policy_msg, None).ok
    teams_parent_adm = list(resource_setup.service.GetOwnedTeams(
        bs.EntityId(id=pt_adm), None
    ))
    assert len(teams_parent_adm) == 1
    teams_child_adm = list(resource_setup.service.GetOwnedTeams(
        bs.EntityId(id=ct_adm), None
    ))
    assert len(teams_child_adm) == 1

def test_push_event_on_approve(resource_setup: ResourceSetup):
    meeting = Meeting(1, 1)
    msg = bs.MeetingInfo(
        id=-1,
        creator=meeting.creator,
        team=meeting.team,
        desc=meeting.desc,
        time=meeting.time
    )
    meeting_id = resource_setup.service.CreateMeeting(msg, None).id
    assert resource_setup.calendar.timesPushed == 0
    approve_msg = bs.EntityId(id=meeting_id)
    assert resource_setup.service.ApproveMeeting(approve_msg, None).ok
    assert resource_setup.calendar.timesPushed == 1
