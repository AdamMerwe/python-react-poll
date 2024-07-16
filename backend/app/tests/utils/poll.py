from sqlmodel import Session

from app import crud
from app.models import Poll, PollCreate
from app.tests.utils.user import create_random_user
from app.tests.utils.utils import random_lower_string


def create_random_poll(db: Session) -> Poll:
    user = create_random_user(db)
    owner_id = user.id
    assert owner_id is not None
    title = random_lower_string()
    description = random_lower_string()
    poll_in = PollCreate(title=title, description=description)
    return crud.create_poll(session=db, poll_in=poll_in, owner_id=owner_id)
