from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from ..database import get_session
from ..dependencies import ensure_user_exists, require_role
from ..models import LedgerEntry, LedgerEntryType, RoleEnum, User

router = APIRouter(prefix="/ledger", tags=["ledger"])


def _apply_balance(session: Session, entry: LedgerEntry) -> None:
    if entry.user_id is None:
        return
    user = session.get(User, entry.user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found for ledger entry")
    if entry.entry_type == LedgerEntryType.debit:
        user.balance_cents -= entry.amount_cents
    else:
        user.balance_cents += entry.amount_cents
    session.add(user)


@router.get("", response_model=list[LedgerEntry])
def list_entries(session: Session = Depends(get_session)) -> list[LedgerEntry]:
    return session.exec(select(LedgerEntry).order_by(LedgerEntry.created_at.desc())).all()


@router.post("", response_model=LedgerEntry, status_code=status.HTTP_201_CREATED)
def create_entry(
    entry: LedgerEntry,
    session: Session = Depends(get_session),
    _: User = Depends(require_role((RoleEnum.admin, RoleEnum.treasurer))),
) -> LedgerEntry:
    session.add(entry)
    _apply_balance(session, entry)
    session.commit()
    session.refresh(entry)
    return entry


@router.get("/{user_id}/balance", response_model=dict)
def balance(user_id: int, session: Session = Depends(get_session)) -> dict:
    user = ensure_user_exists(session, user_id)
    return {"user_id": user.id, "balance_cents": user.balance_cents}
