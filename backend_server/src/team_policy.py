import backend_service_pb2 as bs


class TeamPolicy:
    def __init__(self):
        self.allow_users_to_create_meetings = True
        self.need_approve_for_meeting_creation = False


def policy_from_msg(msg: bs.TeamPolicy) -> TeamPolicy:
    policy = TeamPolicy()
    policy.need_approve_for_meeting_creation = msg.needApproveForMeetingCreation
    policy.allow_users_to_create_meetings = msg.allowUsersToCreateMeetings
    return policy
