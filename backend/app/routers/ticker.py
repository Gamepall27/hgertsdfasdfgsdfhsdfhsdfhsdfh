from collections import Counter

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from ..database import get_session
from ..dependencies import get_current_user, require_role
from ..models import Event, LiveTickerEvent, RoleEnum, User

router = APIRouter(prefix="/ticker", tags=["ticker"])


@router.post("/{event_id}", response_model=LiveTickerEvent, status_code=status.HTTP_201_CREATED)
def add_ticker_event(
    event_id: int,
    ticker_event: LiveTickerEvent,
    session: Session = Depends(get_session),
    _: User = Depends(require_role((RoleEnum.admin, RoleEnum.treasurer))),
) -> LiveTickerEvent:
    event = session.get(Event, event_id)
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")
    ticker_event.event_id = event_id
    session.add(ticker_event)
    session.commit()
    session.refresh(ticker_event)
    return ticker_event


@router.get("/{event_id}", response_model=dict)
def list_ticker_events(
    event_id: int,
    session: Session = Depends(get_session),
    _: User = Depends(get_current_user),
) -> dict:
    event = session.get(Event, event_id)
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")
    entries = session.exec(select(LiveTickerEvent).where(LiveTickerEvent.event_id == event_id)).all()
    score = Counter()
    for e in entries:
        if e.event_type.lower() == "goal":
            team = e.team_for or "home"
            score[team] += 1
    return {"events": entries, "score": dict(score)}
