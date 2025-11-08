from data_warehouse.db_manager import DBManager

db = DBManager()

def login_enter():
    print("\n--- User Login ---")
    email = input("Email: ").strip().lower()
    password = input("Password: ").strip()
    
    # Check student first
    student = db.get_student_by_email(email)
    if student and student[3] == password:
        print(f"Welcome student {student[1]}!")
        return "student", student
    
    # Check teacher
    teacher = db.get_teacher_by_email(email)
    if teacher and teacher[3] == password:
        print(f"Welcome teacher {teacher[1]}!")
        return "teacher", teacher
    
    print("Invalid email or password!")
    return None, None
