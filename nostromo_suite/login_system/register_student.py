import re
from core.anti_bot import eula_agreement, mini_captcha
from data_warehouse.db_manager import DBManager

db = DBManager()

COURSES = [
    "Computer Science",
    "Computer Engineering",
    "Systems Analysis and Development",
    "Hardware Engineering",
    "Mechatronics",
    "Electrical Engineering",
    "Mechanical Engineering"
]

def validate_password(password: str) -> bool:
    """Validate password: min 8 chars, 1 upper, 1 lower, 1 number, no spaces."""
    if len(password) < 8:
        return False
    if re.search(r"\s", password):
        return False
    if not re.search(r"[A-Z]", password):
        return False
    if not re.search(r"[a-z]", password):
        return False
    if not re.search(r"\d", password):
        return False
    return True

def validate_ra(ra: str) -> bool:
    """Simple RA validation: last 4 digits must be '7749'."""
    return ra[-4:] == "7749"

def register_student():
    print("\n--- Student Registration ---")
    name = input("Name: ").strip()
    email = input("Email: ").strip().lower()
    
    # Password
    while True:
        password = input("Password: ").strip()
        if validate_password(password):
            break
        print("Password invalid! Must be at least 8 characters, 1 upper, 1 lower, 1 number, no spaces.")
    
    # RA
    while True:
        ra = input("Student Registration Number (RA): ").strip()
        if validate_ra(ra):
            break
        print("RA invalid! Last 4 digits must be '7749'.")
    
    # Course
    print("Available courses:")
    for i, course in enumerate(COURSES, 1):
        print(f"{i}. {course}")
    while True:
        choice = input("Select course number: ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(COURSES):
            course = COURSES[int(choice)-1]
            break
        print("Invalid course selection.")
    
    # Period
    while True:
        period = input("Period (1-10): ").strip()
        if period.isdigit() and 1 <= int(period) <= 10:
            period = int(period)
            break
        print("Invalid period.")
    
    # EULA & CAPTCHA
    eula_text = "Lorem ipsum dolor sit amet, consectetur adipiscing elit."
    agreed_eula = eula_agreement(eula_text)
    passed_captcha = mini_captcha()
    
    if not agreed_eula:
        print("You must agree to the EULA to register.")
        return
    if not passed_captcha:
        print("CAPTCHA failed. Registration aborted.")
        return
    
    # Insert into DB
    success = db.insert_student({
        "name": name,
        "email": email,
        "password": password,
        "ra": ra,
        "course": course,
        "period": period,
        "agreed_eula": agreed_eula,
        "passed_captcha": passed_captcha
    })
    
    if success:
        print(f"Student {name} registered successfully!")
    else:
        print("Failed to register student. Email or RA may already exist.")
