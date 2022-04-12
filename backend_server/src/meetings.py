import yaml

from typing import Iterable, Optional

import backend_service_pb2 as bs

from icollection import ICollection


class Meeting:
    def __init__(self, _creator: int, _team: int):
        self.approved = False
        self.id = -1
        self.creator = _creator
        self.team = _team
        self.desc = ''
        self.time = 0
        self.participants = [_creator]

    def __eq__(self, other) -> bool:
        return (
            self.approved == other.approved 
            and self.creator == other.creator
            and self.team == other.team
            and self.desc == other.desc
            and self.time == other.time
            and self.participants == other.participants
        )

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
    
    def serialize(self):
        return {
            '_id': self.id,
            'approved': self.approved,
            'creator': self.creator,
            'team': self.team,
            'desc': self.desc,
            'time': self.time,
            'participants': self.participants
        }


def meeting_from_msg(info: bs.MeetingInfo) -> Meeting:
    meeting = Meeting(info.creator, info.team)
    meeting.id = info.id
    meeting.desc = info.desc
    meeting.time = info.time
    return meeting


def meeting_from_mongo(info) -> Meeting:
    meeting = Meeting(info['creator'], info['team'])
    meeting.id = info['_id']
    meeting.time = info['time']
    meeting.desc = info['desc']
    meeting.participants = info['participants']
    meeting.approved = info['approved']
    return meeting


class MeetingsRepo:
    def __init__(self, collection: ICollection):
        self.__collection = collection

    def add_meeting(self, meeting: Meeting):
        from random import randint
        meeting.id = randint(0, int(9e10))
        self.__collection.insert_one(meeting.serialize())
        return meeting.id

    def update_meeting(self, meeting: Meeting):
        if meeting.desc is not None and meeting.desc != '':
            self.__collection.set_one(meeting.id, 'desc', meeting.desc)
        if meeting.time is not None and meeting.time != -1:
            self.__collection.set_one(meeting.id, 'time', meeting.time)

    def get_meetings_by_owner(self, owner: int) -> Iterable[Meeting]:
        cursor = self.__collection.find_many({'creator': owner, 'approved': True})
        for item in cursor:
            yield meeting_from_mongo(item)

    def add_participant(self, meeting_id: int, user_id: int):
        self.__collection.push_to_one(meeting_id, 'participants', user_id)

    def get_meeting(self, meeting_id: int) -> Optional[Meeting]:
        m = self.__collection.find_one({'_id': meeting_id})
        if m is None:
            return None
        return meeting_from_mongo(m)

    def approve_meeting(self, meeting_id: int):
        self.__collection.set_one(meeting_id, 'approved', True)

    def get_meetings_by_group(self, group_id: int) -> Iterable[Meeting]:
        cursor = self.__collection.find_many({'team': group_id, 'approved': True})
        for item in cursor:
            yield meeting_from_mongo(item)

    def get_meetings_my_user(self, user_id: int) -> Iterable[Meeting]:
        cursor = self.__collection.find_many({'approved': True, 'participants': user_id})
        for item in cursor:
            yield meeting_from_mongo(item)

