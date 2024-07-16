from typing import Any

from fastapi import APIRouter, HTTPException
from sqlmodel import func, select

from app.api.deps import CurrentUser, SessionDep
from app.models import Poll, PollCreate, PollPublic, PollPublic, PollUpdate, Message

router = APIRouter()


@router.get("/", response_model=PollPublic)
def read_polls(
    session: SessionDep, current_user: CurrentUser, skip: int = 0, limit: int = 100
) -> Any:
    """
    Retrieve polls.
    """

    if current_user.is_superuser:
        count_statement = select(func.count()).select_from(Poll)
        count = session.exec(count_statement).one()
        statement = select(Poll).offset(skip).limit(limit)
        polls = session.exec(statement).all()
    else:
        count_statement = (
            select(func.count())
            .select_from(Poll)
            .where(Poll.owner_id == current_user.id)
        )
        count = session.exec(count_statement).one()
        statement = (
            select(Poll)
            .where(Poll.owner_id == current_user.id)
            .offset(skip)
            .limit(limit)
        )
        polls = session.exec(statement).all()

    return PollPublic(data=polls, count=count)


@router.get("/{id}", response_model=PollPublic)
def read_poll(session: SessionDep, current_user: CurrentUser, id: int) -> Any:
    """
    Get poll by ID.
    """
    poll = session.get(Poll, id)
    if not poll:
        raise HTTPException(status_code=404, detail="Poll not found")
    if not current_user.is_superuser and (poll.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    return poll


@router.post("/", response_model=PollPublic)
def create_poll(
    *, session: SessionDep, current_user: CurrentUser, poll_in: PollCreate
) -> Any:
    """
    Create new poll.
    """
    poll = Poll.model_validate(poll_in, update={"owner_id": current_user.id})
    session.add(poll)
    session.commit()
    session.refresh(poll)
    return poll


@router.put("/{id}", response_model=PollPublic)
def update_poll(
    *, session: SessionDep, current_user: CurrentUser, id: int, poll_in: PollUpdate
) -> Any:
    """
    Update a poll.
    """
    poll = session.get(Poll, id)
    if not poll:
        raise HTTPException(status_code=404, detail="Poll not found")
    if not current_user.is_superuser and (poll.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    update_dict = poll_in.model_dump(exclude_unset=True)
    poll.sqlmodel_update(update_dict)
    session.add(poll)
    session.commit()
    session.refresh(poll)
    return poll


@router.delete("/{id}")
def delete_poll(session: SessionDep, current_user: CurrentUser, id: int) -> Message:
    """
    Delete a poll.
    """
    poll = session.get(Poll, id)
    if not poll:
        raise HTTPException(status_code=404, detail="Poll not found")
    if not current_user.is_superuser and (poll.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    session.delete(poll)
    session.commit()
    return Message(message="Poll deleted successfully")
