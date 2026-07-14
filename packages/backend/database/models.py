import uuid
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from packages.backend.database.session import Base


def generate_uuid():
    return str(uuid.uuid4())


class Kindergarten(Base):
    __tablename__ = "kindergartens"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(100), nullable=False)
    timezone = Column(String(50), default="Asia/Shanghai")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Semester(Base):
    __tablename__ = "semesters"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(100), nullable=False)
    start_date = Column(String(10), nullable=False)
    end_date = Column(String(10), nullable=False)
    is_current = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    kindergarten_id = Column(String(36), ForeignKey("kindergartens.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    kindergarten = relationship("Kindergarten")


class AgeGroup(Base):
    __tablename__ = "age_groups"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(50), nullable=False)
    sort_order = Column(Integer, default=0)
    kindergarten_id = Column(String(36), ForeignKey("kindergartens.id"), nullable=False)

    kindergarten = relationship("Kindergarten")


class Class(Base):
    __tablename__ = "classes"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(100), nullable=False)
    age_group_id = Column(String(36), ForeignKey("age_groups.id"), nullable=False)
    kindergarten_id = Column(String(36), ForeignKey("kindergartens.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    age_group = relationship("AgeGroup")
    kindergarten = relationship("Kindergarten")


class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    username = Column(String(50), nullable=False, unique=True)
    phone = Column(String(20), nullable=True, unique=True)
    email = Column(String(100), nullable=True, unique=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=True)
    is_active = Column(Boolean, default=True)
    kindergarten_id = Column(String(36), ForeignKey("kindergartens.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    kindergarten = relationship("Kindergarten")


class Role(Base):
    __tablename__ = "roles"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(50), nullable=False)
    description = Column(String(200), nullable=True)
    kindergarten_id = Column(String(36), ForeignKey("kindergartens.id"), nullable=False)

    kindergarten = relationship("Kindergarten")


class UserRole(Base):
    __tablename__ = "user_roles"

    user_id = Column(String(36), ForeignKey("users.id"), primary_key=True)
    role_id = Column(String(36), ForeignKey("roles.id"), primary_key=True)
    assigned_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User")
    role = relationship("Role")


class ClassTeacher(Base):
    __tablename__ = "class_teachers"

    class_id = Column(String(36), ForeignKey("classes.id"), primary_key=True)
    teacher_id = Column(String(36), ForeignKey("users.id"), primary_key=True)
    is_main = Column(Boolean, default=False)
    assigned_at = Column(DateTime, default=datetime.utcnow)

    class_ = relationship("Class")
    teacher = relationship("User")


class Area(Base):
    __tablename__ = "areas"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(100), nullable=False)
    category = Column(String(20), nullable=False)
    sort_order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    class_id = Column(String(36), ForeignKey("classes.id"), nullable=False)
    kindergarten_id = Column(String(36), ForeignKey("kindergartens.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    class_ = relationship("Class")
    kindergarten = relationship("Kindergarten")
