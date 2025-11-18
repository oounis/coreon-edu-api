from app.db.session import SessionLocal
from app import models


def run():
    db = SessionLocal()

    try:
        # ---------------------------
        # 1) Create School if missing
        # ---------------------------
        school = (
            db.query(models.School)
            .filter(models.School.code == "SCH-1")
            .first()
        )

        if not school:
            school = models.School(
                name="Kogia Demo School",
                code="SCH-1",
                address="Demo Street 1",
                city="Demo City",
                country="Demo Country",
                is_active=True,
            )
            db.add(school)
            db.flush()  # get school.id

        # ---------------------------
        # 2) Create Grade if missing
        # ---------------------------
        grade = (
            db.query(models.Grade)
            .filter(
                models.Grade.school_id == school.id,
                models.Grade.name == "Grade 1",
            )
            .first()
        )

        if not grade:
            grade = models.Grade(
                name="Grade 1",
                school_id=school.id,
            )
            db.add(grade)
            db.flush()

        # ---------------------------
        # 3) Create Classroom if missing
        # ---------------------------
        classroom = (
            db.query(models.Classroom)
            .filter(
                models.Classroom.grade_id == grade.id,
                models.Classroom.name == "Class A",
            )
            .first()
        )

        if not classroom:
            classroom = models.Classroom(
                name="Class A",
                grade_id=grade.id,
            )
            db.add(classroom)
            db.flush()

        # ---------------------------
        # 4) Create a demo student
        # ---------------------------
        student = (
            db.query(models.Student)
            .filter(models.Student.name == "John Demo")
            .first()
        )

        if not student:
            student = models.Student(
                name="John Demo",
                gender="male",
                classroom_id=classroom.id,
                is_active=True,
                email="john.demo@example.com",
                admission_number="ADM-0001",
            )
            db.add(student)

        # ---------------------------
        # 5) Create core departments
        # ---------------------------
        dept_defs = [
            ("transport", "Transport Department"),
            ("medical", "Medical / Nursing"),
            ("external_relations", "External Relations"),
            ("vendors", "Vendors & Partners"),
        ]

        for code, name in dept_defs:
            existing = (
                db.query(models.Department)
                .filter(
                    models.Department.school_id == school.id,
                    models.Department.code == code,
                )
                .first()
            )
            if not existing:
                d = models.Department(
                    school_id=school.id,
                    code=code,
                    name=name,
                    is_active=True,
                )
                db.add(d)

        db.commit()
        print("✅ Demo school / grade / classroom / student / departments seeded.")

    except Exception as e:
        db.rollback()
        print("❌ Error while seeding:", e)
        raise
    finally:
        db.close()


if __name__ == "__main__":
    run()
