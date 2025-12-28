from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from ..database import get_session
from ..dependencies import get_current_user, require_role
from ..models import Event, EventResponse, EventType, ResponseStatus, RoleEnum, User

router = APIRouter(prefix="/events", tags=["events"])


@router.get("", response_model=list[Event])
def list_events(session: Session = Depends(get_session)) -> list[Event]:
    return session.exec(select(Event)).all()


@router.post("", response_model=Event, status_code=status.HTTP_201_CREATED)
def create_event(
    event: Event,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_role((RoleEnum.admin, RoleEnum.treasurer))),
) -> Event:
    event.created_by = current_user.id
    session.add(event)
    session.commit()
    session.refresh(event)
    return event


@router.post("/{event_id}/respond", response_model=EventResponse)
def respond_to_event(
    event_id: int,
    response: ResponseStatus,
    note: str | None = None,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> EventResponse:
    event = session.get(Event, event_id)
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")

    existing = session.exec(
        select(EventResponse).where(EventResponse.event_id == event_id, EventResponse.user_id == current_user.id)
    ).first()
    if existing:
        existing.response = response
        existing.note = note
        session.add(existing)
        session.commit()
        session.refresh(existing)
        return existing

    event_response = EventResponse(event_id=event_id, user_id=current_user.id, response=response, note=note)
    session.add(event_response)
    session.commit()
    session.refresh(event_response)
    return event_response


@router.get("/{event_id}/responses", response_model=list[EventResponse])
def list_responses(event_id: int, session: Session = Depends(get_session)) -> list[EventResponse]:
    event = session.get(Event, event_id)
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")
    return session.exec(select(EventResponse).where(EventResponse.event_id == event_id)).all()
