from login_system.register_student import register_student
from login_system.register_teacher import register_teacher
from login_system.login_enter import login_enter

def start_up():
    while True:
        print("\n--- Nostromo Suite ---")
        print("1. Register User")
        print("2. Login")
        print("3. Exit")
        choice = input("Select option: ").strip()
        
        if choice == "1":
            user_type = input("Register as (student/teacher): ").strip().lower()
            if user_type == "student":
                register_student()
            elif user_type == "teacher":
                register_teacher()
            else:
                print("Invalid type!")
        elif choice == "2":
            login_enter()
        elif choice == "3":
            print("Exiting...")
            break
        else:
            print("Invalid option!")

if __name__ == "__main__":
    start_up()
