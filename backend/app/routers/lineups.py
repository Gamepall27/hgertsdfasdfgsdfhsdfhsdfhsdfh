from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from ..database import get_session
from ..dependencies import ensure_user_exists, require_role
from ..models import Event, Lineup, LineupSlot, RoleEnum, User

router = APIRouter(prefix="/lineups", tags=["lineups"])


@router.post("", response_model=Lineup, status_code=status.HTTP_201_CREATED)
def create_lineup(
    lineup: Lineup,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_role((RoleEnum.admin, RoleEnum.treasurer))),
) -> Lineup:
    event = session.get(Event, lineup.event_id)
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")
    lineup.created_by = current_user.id
    session.add(lineup)
    session.commit()
    session.refresh(lineup)
    return lineup


@router.post("/{lineup_id}/slots", response_model=LineupSlot, status_code=status.HTTP_201_CREATED)
def add_slot(
    lineup_id: int,
    slot: LineupSlot,
    session: Session = Depends(get_session),
    _: User = Depends(require_role((RoleEnum.admin, RoleEnum.treasurer))),
) -> LineupSlot:
    lineup = session.get(Lineup, lineup_id)
    if not lineup:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lineup not found")
    ensure_user_exists(session, slot.user_id)
    slot.lineup_id = lineup_id
    session.add(slot)
    session.commit()
    session.refresh(slot)
    return slot


@router.get("/{lineup_id}", response_model=dict)
def get_lineup(lineup_id: int, session: Session = Depends(get_session)) -> dict:
    lineup = session.get(Lineup, lineup_id)
    if not lineup:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lineup not found")
    slots = session.exec(select(LineupSlot).where(LineupSlot.lineup_id == lineup_id)).all()
    return {"lineup": lineup, "slots": slots}
