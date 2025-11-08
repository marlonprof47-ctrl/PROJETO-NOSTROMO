import re

# Lista de cursos (movida para cá)
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
    if re.search(r"\s", password): # Contém espaço
        return False
    if not re.search(r"[A-Z]", password): # Não tem maiúscula
        return False
    if not re.search(r"[a-z]", password): # Não tem minúscula
        return False
    if not re.search(r"\d", password): # Não tem número
        return False
    return True

def validate_ra(ra: str) -> bool:
    """Simple RA validation: last 4 digits must be '7749'."""
    if not ra or len(ra) < 4:
        return False
    return ra.strip()[-4:] == "7749"

def validate_registration_number(reg_number: str) -> bool:
    """Validate teacher registration number: exactly 9 digits."""
    if not reg_number:
        return False
    return len(reg_number.strip()) == 9 and reg_number.strip().isdigit()