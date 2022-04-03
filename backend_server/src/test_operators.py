from teams import Team
from meetings import Meeting


def team_eq_ignore_id(a: Team, b: Team) -> bool:
    return (
        a.owner == b.owner
        and a.members == b.members
        and a.parent == b.parent
        and a.children == b.children
        and a.policy == b.policy
    )

def meeting_eq_ignore_id(a: Meeting, b: Meeting) -> bool:
    return (
        a.approved == b.approved
        and a.creator == b.creator
        and a.desc == b.desc
        and a.participants == b.participants
        and a.team == b.team
        and a.time == b.time
    )
