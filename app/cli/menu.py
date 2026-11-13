from app.core.config import settings
from app.core.exceptions import StudentSystemError
from app.repositories import (
    CourseRepository,
    EnrollmentRepository,
    StudentRepository,
    UserRepository,
)
from app.services import AuthService, CourseService, ReportService, StudentService
from app.utils import build_message, format_courses, format_students


def build_services():
    """Composition root: construct repositories and services."""
    users = UserRepository()
    students = StudentRepository()
    courses = CourseRepository()
    enrollments = EnrollmentRepository()
    return AuthService(users), students, courses, enrollments


def run_cli() -> None:
    auth, student_repo, course_repo, enrollment_repo = build_services()
    print(f"=== {settings.app_name} ===")

    while True:
        try:
            print(
                "\n1) Register  2) Login  3) Students  4) Add student\n"
                "5) Courses   6) Add course  7) Enroll    8) Add grade\n"
                "9) Average   10) Top       11) Logout  0) Exit"
            )
            choice = input("> ").strip()

            if choice == "0":
                return
            if choice == "1":
                user = auth.register(input("Username: "), input("Password: "))
                print(f"Registered: {user.username}")
            elif choice == "2":
                user = auth.login(input("Username: "), input("Password: "))
                print(f"Logged in as {user.username} ({user.role.value})")
            elif choice == "11":
                auth.logout()
                print("Logged out")
            else:
                authenticated_menu(
                    choice, auth, student_repo, course_repo, enrollment_repo
                )
        except (StudentSystemError, ValueError) as exc:
            print(f"ERROR: {exc}")
        except KeyboardInterrupt:
            print("\nGoodbye!")
            return


def authenticated_menu(choice, auth, student_repo, course_repo, enrollment_repo):
    if auth.current_user is None:
        print("Please login first.")
        return

    ss = StudentService(student_repo, auth.current_user)
    cs = CourseService(course_repo, enrollment_repo, student_repo, auth.current_user)
    rs = ReportService(student_repo, course_repo, enrollment_repo)

    if choice == "3":
        print(format_students(ss.list_students()))
    elif choice == "4":
        student = ss.add_student(input("Name: "), input("Student no: "), input("Major: "))
        print(f"Created {student.student_no}")
    elif choice == "5":
        print(format_courses(cs.list_courses()))
    elif choice == "6":
        course = cs.add_course(input("Code: "), input("Name: "), int(input("Credits: ")))
        print(f"Created {course.code}")
    elif choice == "7":
        enrollment = cs.enroll(input("Student no: "), input("Course code: "))
        print(f"Enrollment {enrollment.id[:8]}")
    elif choice == "8":
        add_grade(enrollment_repo, student_repo, course_repo)
    elif choice == "9":
        no = input("Student no: ")
        avg = rs.student_average(no)
        message = build_message("REPORT", suffix="!")
        print(message("student average", student_no=no, average=round(avg, 2)))
    elif choice == "10":
        for student, avg in rs.top_students():
            print(f"{student.student_no:<10} | {student.name:<25} | {avg:.2f}")
    else:
        print("Unknown choice")


def add_grade(enrollment_repo, student_repo, course_repo):
    student = student_repo.get_by_number(input("Student no: ").strip())
    course = course_repo.get_by_code(input("Course code: ").strip().upper())
    if student is None or course is None:
        raise ValueError("Student or course does not exist")

    enrollment = enrollment_repo.find(student.id, course.id)
    if enrollment is None:
        raise ValueError("Student is not enrolled in this course")

    grade = float(input("Grade (0-100): "))
    if not 0 <= grade <= 100:
        raise ValueError("Grade must be between 0 and 100")

    enrollment.grade = grade
    enrollment_repo.save(enrollment)
    print("Grade saved.")
