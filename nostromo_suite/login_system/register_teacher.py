import re
from core.anti_bot import eula_agreement, mini_captcha
from data_warehouse.db_manager import DBManager

db = DBManager()

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

def validate_registration_number(reg_number: str) -> bool:
    """Validate teacher registration number: exactly 9 digits."""
    return len(reg_number) == 9 and reg_number.isdigit()

def register_teacher():
    print("\n--- Teacher Registration ---")
    name = input("Name: ").strip()
    email = input("Email: ").strip().lower()
    
    # Password
    while True:
        password = input("Password: ").strip()
        if validate_password(password):
            break
        print("Password invalid! Must be at least 8 characters, 1 upper, 1 lower, 1 number, no spaces.")
    
    # Registration number
    while True:
        reg_number = input("Registration Number (9 digits): ").strip()
        if validate_registration_number(reg_number):
            break
        print("Invalid registration number!")
    
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
    success = db.insert_teacher({
        "name": name,
        "email": email,
        "password": password,
        "registration_number": reg_number,
        "agreed_eula": agreed_eula,
        "passed_captcha": passed_captcha
    })
    
    if success:
        print(f"Teacher {name} registered successfully!")
    else:
        print("Failed to register teacher. Email or registration number may already exist.")