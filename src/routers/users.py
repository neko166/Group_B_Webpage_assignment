from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session, joinedload
from database import get_db
import auth
from exceptions import AppException, ErrorCode
import models
import schemas

router = APIRouter()


# ── 認証 ──────────────────────────────────────────
@router.post("/login", response_model=schemas.Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == form_data.username).first()
    if not db_user or not auth.verify_password(form_data.password, db_user.password):
        raise AppException(ErrorCode.INCORRECT_USERNAME_OR_PASSWORD)
    access_token = auth.create_access_token(data={"sub": db_user.email})
    return {"access_token": access_token, "token_type": "bearer"}


# ── ユーザー ──────────────────────────────────────
@router.get("/{user_id}", response_model=schemas.UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.patch("/{user_id}", response_model=schemas.UserResponse)
def update_user(user_id: int, payload: schemas.UserUpdate, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(user, field, value)
    db.commit()
    db.refresh(user)
    return user


# ── スキルマスタ ──────────────────────────────────
@router.get("/skills/master", response_model=list[schemas.SkillResponse])
def list_skills(db: Session = Depends(get_db)):
    return db.query(models.Skill).all()


@router.post("/skills/master", response_model=schemas.SkillResponse)
def create_skill(payload: schemas.SkillCreate, db: Session = Depends(get_db)):
    existing = db.query(models.Skill).filter(models.Skill.skill_name == payload.skill_name).first()
    if existing:
        return existing
    skill = models.Skill(**payload.model_dump())
    db.add(skill)
    db.commit()
    db.refresh(skill)
    return skill


# ── ユーザースキル ────────────────────────────────
@router.get("/{user_id}/skills", response_model=list[schemas.UserSkillResponse])
def get_user_skills(user_id: int, db: Session = Depends(get_db)):
    rows = (
        db.query(models.UserSkill)
        .options(joinedload(models.UserSkill.skill))
        .filter(models.UserSkill.user_id == user_id)
        .all()
    )
    return [
        schemas.UserSkillResponse(
            id=r.id,
            skill_id=r.skill_id,
            skill_name=r.skill.skill_name,
            category=r.skill.category,
            skill_level=r.skill_level,
        )
        for r in rows
    ]


@router.post("/{user_id}/skills", response_model=schemas.UserSkillResponse)
def add_user_skill(user_id: int, payload: schemas.UserSkillCreate, db: Session = Depends(get_db)):
    skill = db.query(models.Skill).filter(models.Skill.skill_id == payload.skill_id).first()
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")
    existing = (
        db.query(models.UserSkill)
        .filter(models.UserSkill.user_id == user_id, models.UserSkill.skill_id == payload.skill_id)
        .first()
    )
    if existing:
        raise HTTPException(status_code=409, detail="Skill already added")
    us = models.UserSkill(user_id=user_id, skill_id=payload.skill_id, skill_level=payload.skill_level)
    db.add(us)
    db.commit()
    db.refresh(us)
    return schemas.UserSkillResponse(
        id=us.id, skill_id=us.skill_id,
        skill_name=skill.skill_name, category=skill.category,
        skill_level=us.skill_level,
    )


@router.patch("/{user_id}/skills/{user_skill_id}", response_model=schemas.UserSkillResponse)
def update_user_skill(user_id: int, user_skill_id: int, payload: schemas.UserSkillUpdate, db: Session = Depends(get_db)):
    us = db.query(models.UserSkill).filter(
        models.UserSkill.id == user_skill_id,
        models.UserSkill.user_id == user_id,
    ).first()
    if not us:
        raise HTTPException(status_code=404, detail="UserSkill not found")
    us.skill_level = payload.skill_level
    db.commit()
    db.refresh(us)
    return schemas.UserSkillResponse(
        id=us.id, skill_id=us.skill_id,
        skill_name=us.skill.skill_name, category=us.skill.category,
        skill_level=us.skill_level,
    )


@router.delete("/{user_id}/skills/{user_skill_id}", status_code=204)
def delete_user_skill(user_id: int, user_skill_id: int, db: Session = Depends(get_db)):
    us = db.query(models.UserSkill).filter(
        models.UserSkill.id == user_skill_id,
        models.UserSkill.user_id == user_id,
    ).first()
    if not us:
        raise HTTPException(status_code=404, detail="UserSkill not found")
    db.delete(us)
    db.commit()


# ── 職務経歴 ──────────────────────────────────────
@router.get("/{user_id}/careers", response_model=list[schemas.CareerHistoryResponse])
def get_user_careers(user_id: int, db: Session = Depends(get_db)):
    careers = (
        db.query(models.CareerHistory)
        .filter(models.CareerHistory.user_id == user_id)
        .order_by(models.CareerHistory.period_start.desc())
        .all()
    )
    return careers


@router.post("/{user_id}/careers", response_model=schemas.CareerHistoryResponse)
def add_career(user_id: int, payload: schemas.CareerHistoryCreate, db: Session = Depends(get_db)):
    career = models.CareerHistory(user_id=user_id, **payload.model_dump())
    db.add(career)
    db.commit()
    db.refresh(career)
    return career


@router.patch("/{user_id}/careers/{career_id}", response_model=schemas.CareerHistoryResponse)
def update_career(user_id: int, career_id: int, payload: schemas.CareerHistoryUpdate, db: Session = Depends(get_db)):
    career = db.query(models.CareerHistory).filter(
        models.CareerHistory.career_id == career_id,
        models.CareerHistory.user_id == user_id,
    ).first()
    if not career:
        raise HTTPException(status_code=404, detail="Career not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(career, field, value)
    db.commit()
    db.refresh(career)
    return career


@router.delete("/{user_id}/careers/{career_id}", status_code=204)
def delete_career(user_id: int, career_id: int, db: Session = Depends(get_db)):
    career = db.query(models.CareerHistory).filter(
        models.CareerHistory.career_id == career_id,
        models.CareerHistory.user_id == user_id,
    ).first()
    if not career:
        raise HTTPException(status_code=404, detail="Career not found")
    db.delete(career)
    db.commit()
