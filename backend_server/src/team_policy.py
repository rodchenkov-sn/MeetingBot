import backend_service_pb2 as bs


class TeamPolicy:
    def __init__(self):
        self.allow_users_to_create_meetings = True
        self.need_approve_for_meeting_creation = False
        self.propagate_policy = False
        self.parent_visible = True
        self.propagate_admin = True

    def __eq__(self, other):
        return (
            self.allow_users_to_create_meetings == other.allow_users_to_create_meetings
            and self.need_approve_for_meeting_creation == other.need_approve_for_meeting_creation
            and self.parent_visible == other.parent_visible
            and self.propagate_admin == other.propagate_admin
            and self.propagate_policy == other.propagate_policy
        )


def policy_from_msg(msg: bs.TeamPolicy) -> TeamPolicy:
    policy = TeamPolicy()
    policy.need_approve_for_meeting_creation = msg.needApproveForMeetingCreation
    policy.allow_users_to_create_meetings = msg.allowUsersToCreateMeetings
    policy.propagate_policy = msg.propagatePolicy
    policy.parent_visible = msg.parentVisible
    policy.propagate_admin = msg.propagateAdmin
    return policy
