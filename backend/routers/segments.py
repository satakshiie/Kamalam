# backend/routers/segments.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Segment
from schemas.segment import SegmentResponse, SegmentCreate, SegmentSummary

router = APIRouter()


# ──────────────────────────────────────────────────────────────────────
# GET ALL SEGMENTS
# ──────────────────────────────────────────────────────────────────────
@router.get("/segments", response_model=list[SegmentResponse])
def get_segments(db: Session = Depends(get_db)):
    return db.query(Segment).order_by(Segment.created_at.desc()).all()


# ──────────────────────────────────────────────────────────────────────
# GET SINGLE SEGMENT
# ──────────────────────────────────────────────────────────────────────
@router.get("/segments/{segment_id}", response_model=SegmentResponse)
def get_segment(segment_id: int, db: Session = Depends(get_db)):
    segment = db.query(Segment).filter(Segment.id == segment_id).first()
    if not segment:
        raise HTTPException(status_code=404, detail="Segment not found")
    return segment


# ──────────────────────────────────────────────────────────────────────
# CREATE SEGMENT — manual creation by marketer
# ──────────────────────────────────────────────────────────────────────
@router.post("/segments", response_model=SegmentResponse)
def create_segment(payload: SegmentCreate, db: Session = Depends(get_db)):
    segment = Segment(
        name        = payload.name,
        description = payload.description,
        filters     = payload.filters,
        created_by  = "manual",
    )
    db.add(segment)
    db.commit()
    db.refresh(segment)
    return segment


# ──────────────────────────────────────────────────────────────────────
# GET SEGMENT SUMMARIES — lightweight for campaign creation dropdowns
# ──────────────────────────────────────────────────────────────────────
@router.get("/segments/summary/all", response_model=list[SegmentSummary])
def get_segment_summaries(db: Session = Depends(get_db)):
    return db.query(Segment).order_by(Segment.name).all()