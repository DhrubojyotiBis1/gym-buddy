import enum


class ConversationType(enum.Enum):
    ONE_TO_ONE = "one_to_one"
    GROUP = "group"

class Role(enum.Enum):
    ADMIN = 'admin'
    MEMBER = 'member'

class UserRole(enum.Enum):
    trainer = "trainer"
    trainee = "trainee"
    admin = "admin"
