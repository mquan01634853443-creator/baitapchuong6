from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

TEXT = {"Content-Type": "text/plain; charset=utf-8"}


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)

app = Flask(__name__)
app.config["SECRET_KEY"] = "dev-chi-dung-khi-phat-trien"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///qlsv.db"
db.init_app(app)


class Student(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    mssv: Mapped[str] = mapped_column(String(10), unique=True)
    name: Mapped[str] = mapped_column(String(100))
    gpa: Mapped[float] = mapped_column(default=0.0)

    def __repr__(self):
        return f"<Student {self.mssv} {self.name}>"


with app.app_context():
    db.create_all()


@app.get("/them-mau")
def them_mau():
    total = db.session.scalar(
        db.select(func.count(Student.id))
    )
    if total > 0:
        return f"Đã có {total} sinh viên, không thêm nữa.", TEXT

    an = Student(mssv="24A100001",
                 name="Nguyễn Minh Khoa", gpa=8.5)
    before = an.id                  # chưa ghi xuống CSDL
    db.session.add(an)              # đưa vào "giỏ" chờ ghi
    db.session.add_all([
        Student(mssv="24A100002", name="Lê Thu Hà", gpa=6.8),
        Student(mssv="24A100003", name="Phạm Quốc Bảo", gpa=9.1),
        Student(mssv="24A100004", name="Võ Ngọc Anh", gpa=4.5),
        Student(mssv="24A100005", name="Trần Gia Huy", gpa=7.4),
    ])
    db.session.commit()             # ghi thật sự
    return (f"Đã thêm 5 sinh viên. id của An: "
            f"trước commit = {before}, "
            f"sau commit = {an.id}"), TEXT


@app.get("/thu-truy-van")
def try_queries():
    if db.session.scalar(
            db.select(func.count(Student.id))) == 0:
        return "Chưa có dữ liệu, hãy mở /them-mau trước.", TEXT
    lines = []

    lines.append(f"1. get(3): {db.session.get(Student, 3)}")
    lines.append(f"2. get(99): {db.session.get(Student, 99)}")

    everyone = db.session.execute(
        db.select(Student)).scalars().all()
    lines.append(f"3. Tất cả: {len(everyone)} sinh viên")

    stmt = (db.select(Student)
            .where(Student.gpa >= 8)
            .order_by(Student.gpa.desc()))
    good = db.session.execute(stmt).scalars().all()
    lines.append(f"4. Điểm >= 8: {good}")

    binh = db.session.scalar(
        db.select(Student).filter_by(mssv="24A100002"))
    lines.append(f"5. MSSV 24A100002: {binh}")

    count = db.session.scalar(
        db.select(func.count(Student.id)))
    avg = db.session.scalar(
        db.select(func.avg(Student.gpa)))
    lines.append(f"6. Số SV: {count}, điểm TB: {avg:.2f}")

    return "\n".join(lines), TEXT
@app.get("/sinh-vien")
def danh_sach():
    students = db.session.execute(
        db.select(Student).order_by(Student.id)
    ).scalars().all()
    return render_template("students.html", students=students)

