from typing import Iterable

import backend_service_pb2 as bs


class Meeting:
    def __init__(self, _creator: int, _team: int):
        self.approved = False
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
            if meeting.creator == owner and meeting.approved:
                yield meeting

    def add_participant(self, meeting_id: int, user_id: int):
        self.__meetings[meeting_id].add_participant(user_id)

    def get_meeting(self, meeting_id: int) -> Meeting:
        return self.__meetings[meeting_id]

    def approve_meeting(self, meeting_id: int):
        self.__meetings[meeting_id].approved = True

    def get_meetings_by_group(self, group_id: int) -> Iterable[Meeting]:
        for meeting in self.__meetings:
            if meeting.team == group_id and meeting.approved:
                yield meeting
