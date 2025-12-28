from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from ..database import get_session
from ..dependencies import ensure_user_exists, require_role
from ..models import AssignedFine, Fine, LedgerEntry, LedgerEntryType, RoleEnum, User

router = APIRouter(prefix="/fines", tags=["fines"])


@router.get("", response_model=list[Fine])
def list_fines(session: Session = Depends(get_session)) -> list[Fine]:
    return session.exec(select(Fine)).all()


@router.post("", response_model=Fine, status_code=status.HTTP_201_CREATED)
def create_fine(
    fine: Fine,
    session: Session = Depends(get_session),
    _: User = Depends(require_role((RoleEnum.admin, RoleEnum.treasurer))),
) -> Fine:
    session.add(fine)
    session.commit()
    session.refresh(fine)
    return fine


@router.post("/assign", response_model=AssignedFine, status_code=status.HTTP_201_CREATED)
def assign_fine(
    assignment: AssignedFine,
    session: Session = Depends(get_session),
    actor: User = Depends(require_role((RoleEnum.admin, RoleEnum.treasurer))),
) -> AssignedFine:
    ensure_user_exists(session, assignment.user_id)
    fine = session.get(Fine, assignment.fine_id)
    if not fine:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Fine not found")

    assignment.assigned_by = actor.id
    session.add(assignment)

    ledger_entry = LedgerEntry(
        user_id=assignment.user_id,
        amount_cents=fine.amount_cents,
        entry_type=LedgerEntryType.debit,
        category="fine",
        description=f"Fine: {fine.title}",
    )
    session.add(ledger_entry)

    user = session.get(User, assignment.user_id)
    if user:
        user.balance_cents -= fine.amount_cents
        session.add(user)

    session.commit()
    session.refresh(assignment)
    return assignment
