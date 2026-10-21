from fastapi import FastAPI
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import engine, Base, SessionLocal
from models import Student, Scholarship, Attendance, Fee, Exam
app = FastAPI(title="Student Management System")
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
Base.metadata.create_all(bind=engine)


class StudentCreate(BaseModel):
    name: str
    roll_number: str
    email: str | None = None
    course: str | None = None
@app.get("/")
def home():
    return {
        "message": "Student Management Backend is running!"
    }


@app.post("/api/students")
def create_student(student: StudentCreate):
    db = SessionLocal()

    try:
        new_student = Student(
            name=student.name,
            roll_number=student.roll_number,
            email=student.email,
            course=student.course
        )

        db.add(new_student)
        db.commit()
        db.refresh(new_student)

        return {
            "message": "Student added successfully!",
            "student": {
                "id": new_student.id,
                "name": new_student.name,
                "roll_number": new_student.roll_number,
                "email": new_student.email,
                "course": new_student.course
            }
        }

    finally:
        db.close()
        
        
@app.post("/api/scholarships")
def create_scholarship(
    student_id: int,
    scholarship_name: str,
    amount: int
):
    db = SessionLocal()

    try:
        new_scholarship = Scholarship(
            student_id=student_id,
            scholarship_name=scholarship_name,
            amount=amount
        )

        db.add(new_scholarship)
        db.commit()
        db.refresh(new_scholarship)

        return {
            "message": "Scholarship added successfully!",
            "id": new_scholarship.id,
            "student_id": new_scholarship.student_id,
            "scholarship_name": new_scholarship.scholarship_name,
            "amount": new_scholarship.amount,
            "status": new_scholarship.status
        }

    finally:
        db.close()
@app.get("/api/students")
def list_students():
    db = SessionLocal()
    try:
        students = db.query(Student).all()
        return [
            {
                "id": s.id,
                "name": s.name,
                "roll_number": s.roll_number,
                "email": s.email,
                "course": s.course,
            }
            for s in students
        ]
    finally:
        db.close()


@app.get("/api/scholarships/{student_id}")
def get_scholarships(student_id: int):
    db = SessionLocal()
    try:
        items = db.query(Scholarship).filter(Scholarship.student_id == student_id).all()
        return [
            {
                "id": i.id,
                "scholarship_name": i.scholarship_name,
                "amount": i.amount,
                "status": i.status,
            }
            for i in items
        ]
    finally:
        db.close()


@app.post("/api/attendance")
def add_attendance(student_id: int, subject: str, total_classes: int, attended_classes: int):
    db = SessionLocal()
    try:
        record = Attendance(
            student_id=student_id,
            subject=subject,
            total_classes=total_classes,
            attended_classes=attended_classes,
        )
        db.add(record)
        db.commit()
        return {"message": "Attendance saved!"}
    finally:
        db.close()


@app.get("/api/attendance/{student_id}")
def get_student_attendance(student_id: int):
    db = SessionLocal()
    try:
        records = db.query(Attendance).filter(Attendance.student_id == student_id).all()
        total = sum(r.total_classes for r in records)
        attended = sum(r.attended_classes for r in records)
        percentage = round((attended / total) * 100, 2) if total else 0
        return {
            "total_classes": total,
            "attended_classes": attended,
            "attendance_percentage": percentage,
            "subjects": [
                {
                    "subject": r.subject,
                    "total_classes": r.total_classes,
                    "attended_classes": r.attended_classes,
                }
                for r in records
            ],
        }
    finally:
        db.close()


@app.post("/api/fees")
def add_fee(student_id: int, amount: int, due_date: str):
    db = SessionLocal()
    try:
        fee = Fee(student_id=student_id, amount=amount, due_date=due_date)
        db.add(fee)
        db.commit()
        db.refresh(fee)
        return {
            "message": "Fee added successfully!",
            "id": fee.id,
            "status": fee.status,
        }
    finally:
        db.close()


@app.get("/api/fees/{student_id}")
def get_fees(student_id: int):
    db = SessionLocal()
    try:
        fees = db.query(Fee).filter(Fee.student_id == student_id).all()
        return [
            {
                "id": f.id,
                "amount": f.amount,
                "due_date": f.due_date,
                "status": f.status,
            }
            for f in fees
        ]
    finally:
        db.close()


@app.post("/api/exams")
def add_exam(subject: str, exam_date: str):
    db = SessionLocal()
    try:
        exam = Exam(subject=subject, exam_date=exam_date)
        db.add(exam)
        db.commit()
        db.refresh(exam)
        return {"message": "Exam added successfully!", "id": exam.id}
    finally:
        db.close()


@app.get("/api/exams")
def get_exams():
    db = SessionLocal()
    try:
        exams = db.query(Exam).order_by(Exam.exam_date).all()
        return [
            {"id": e.id, "subject": e.subject, "exam_date": e.exam_date}
            for e in exams
        ]
    finally:
        db.close()


from datetime import date


@app.get("/api/deadlines/{student_id}")
def get_deadlines(student_id: int):
    db = SessionLocal()
    try:
        today = date.today().isoformat()
        deadlines = []

        fees = (
            db.query(Fee)
            .filter(Fee.student_id == student_id, Fee.status == "Pending", Fee.due_date >= today)
            .all()
        )
        for f in fees:
            deadlines.append({
                "type": "fee",
                "title": f"Fee due: Rs {f.amount}",
                "date": f.due_date,
            })

        exams = db.query(Exam).filter(Exam.exam_date >= today).all()
        for e in exams:
            deadlines.append({
                "type": "exam",
                "title": f"Exam: {e.subject}",
                "date": e.exam_date,
            })

        deadlines.sort(key=lambda d: d["date"])
        return deadlines
    finally:
        db.close()