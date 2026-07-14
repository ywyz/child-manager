import uuid
from datetime import datetime

from sqlalchemy import JSON, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from packages.backend.database.session import Base


def generate_uuid():
    return str(uuid.uuid4())


class LessonPlan(Base):
    __tablename__ = "lesson_plans"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    kindergarten_id = Column(String(36), nullable=False, index=True)
    class_id = Column(String(36), ForeignKey("classes.id"), nullable=False)
    plan_date = Column(String(10), nullable=False)
    semester_id = Column(String(36), ForeignKey("semesters.id"), nullable=False)
    age_group_id = Column(String(36), ForeignKey("age_groups.id"), nullable=False)
    age_group_name = Column(String(50), nullable=False)
    class_name = Column(String(100), nullable=False)
    content = Column(JSON, nullable=False)
    authors = Column(JSON, nullable=False)
    version = Column(Integer, default=1)
    archived_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = ({"schema": None},)


class PlanSnapshot(Base):
    __tablename__ = "plan_snapshots"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    plan_id = Column(String(36), ForeignKey("lesson_plans.id"), nullable=False, index=True)
    content = Column(JSON, nullable=False)
    authors = Column(JSON, nullable=False)
    reason = Column(String(100), nullable=False)
    version = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    plan = relationship("LessonPlan")
