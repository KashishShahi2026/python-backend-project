from sqlalchemy import Column, Integer, String
from database import Base


class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    roll_number = Column(String(30), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=True)
    course = Column(String(100), nullable=True)


class Scholarship(Base):
    __tablename__ = "scholarships"
            
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, nullable=False)
    scholarship_name = Column(String(100), nullable=False)
    amount = Column(Integer, nullable=False)
    status = Column(String(20), default="Pending")


class Attendance(Base):
    __tablename__ = "attendance"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, nullable=False)
    subject = Column(String(100), nullable=False)
    total_classes = Column(Integer, nullable=False)
    attended_classes = Column(Integer, nullable=False)


class Fee(Base):
    __tablename__ = "fees"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, nullable=False)
    amount = Column(Integer, nullable=False)
    due_date = Column(String(20), nullable=False)
    status = Column(String(20), default="Pending")


class Exam(Base):
    __tablename__ = "exams"

    id = Column(Integer, primary_key=True, index=True)
    subject = Column(String(100), nullable=False)
    exam_date = Column(String(20), nullable=False)