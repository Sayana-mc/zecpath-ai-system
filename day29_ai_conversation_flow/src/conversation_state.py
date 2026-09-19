from enum import Enum


class ConversationState(Enum):
    START = "start"
    ASKING = "asking"
    WAITING = "waiting"
    CLARIFICATION = "clarification"
    FOLLOW_UP = "follow_up"
    RETRY = "retry"
    COMPLETED = "completed"
    FAILED = "failed"