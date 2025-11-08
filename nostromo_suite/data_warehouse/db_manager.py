import sqlite3
from pathlib import Path
import os

# Define o caminho para o banco de dados na pasta raiz do projeto (um nível acima de 'data_warehouse')
DB_PATH = Path(__file__).parent.parent / "nostromo_auth.db"

class DBManager:
    def __init__(self, db_path=DB_PATH):
        self.db_path = db_path
        
        # --- LINHAS DE DIAGNÓSTICO ---
        # (Pode remover isto se já tiver confirmado o caminho)
        caminho_absoluto = os.path.abspath(self.db_path)
        print("-------------------------------------------------")
        print(f"!!! O BANCO DE DADOS ESTÁ AQUI: {caminho_absoluto} !!!")
        print("-------------------------------------------------")
        # --- FIM DO DIAGNÓSTICO ---
        
        self._create_tables()

    def _connect(self):
        """Retorna um objeto de conexão SQLite."""
        return sqlite3.connect(self.db_path)

    def _create_tables(self):
        """Cria as tabelas 'students' e 'teachers' se não existirem."""
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS students (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    ra TEXT UNIQUE NOT NULL,
                    course TEXT NOT NULL,
                    period INTEGER NOT NULL,
                    agreed_eula BOOLEAN NOT NULL CHECK (agreed_eula IN (0,1)),
                    passed_captcha BOOLEAN NOT NULL CHECK (passed_captcha IN (0,1)),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS teachers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    registration_number TEXT UNIQUE NOT NULL,
                    agreed_eula BOOLEAN NOT NULL CHECK (agreed_eula IN (0,1)),
                    passed_captcha BOOLEAN NOT NULL CHECK (passed_captcha IN (0,1)),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

    # --- ALUNOS ---
    def insert_student(self, student_data: dict):
        try:
            with self._connect() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO students
                    (name, email, password, ra, course, period, agreed_eula, passed_captcha)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    student_data['name'],
                    student_data['email'],
                    student_data['password'], # Salva a senha (agora o hash)
                    student_data['ra'],
                    student_data['course'],
                    student_data['period'],
                    int(student_data['agreed_eula']),
                    int(student_data['passed_captcha'])
                ))
                conn.commit()
                return True
        except sqlite3.IntegrityError as e:
            print(f"[ERROR] Falha ao inserir aluno: {e}")
            return False

    def get_student_by_email(self, email: str):
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM students WHERE email = ?", (email,))
            return cursor.fetchone()

    def delete_student_by_email(self, email: str):
        """Exclui um aluno com base no email."""
        try:
            with self._connect() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM students WHERE email = ?", (email,))
                conn.commit()
                return True
        except Exception as e:
            print(f"[ERROR] Falha ao excluir aluno: {e}")
            return False

    # --- PROFESSORES ---
    def insert_teacher(self, teacher_data: dict):
        try:
            with self._connect() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO teachers
                    (name, email, password, registration_number, agreed_eula, passed_captcha)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    teacher_data['name'],
                    teacher_data['email'],
                    teacher_data['password'], # Salva a senha (agora o hash)
                    teacher_data['registration_number'],
                    int(teacher_data['agreed_eula']),
                    int(teacher_data['passed_captcha'])
                ))
                conn.commit()
                return True
        except sqlite3.IntegrityError as e:
            print(f"[ERROR] Falha ao inserir professor: {e}")
            return False

    def get_teacher_by_email(self, email: str):
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM teachers WHERE email = ?", (email,))
            return cursor.fetchone()

    def delete_teacher_by_email(self, email: str):
        """Exclui um professor com base no email."""
        try:
            with self._connect() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM teachers WHERE email = ?", (email,))
                conn.commit()
                return True
        except Exception as e:
            print(f"[ERROR] Falha ao excluir professor: {e}")
            return False

    # --- NOVO (PARA O PERFIL JWT) ---
    def get_user_by_email(self, email: str):
        """
        Procura um utilizador em ambas as tabelas (alunos e professores)
        e retorna os seus dados e tipo.
        """
        student = self.get_student_by_email(email)
        if student:
            # Retorna (nome, email, tipo_utilizador)
            return (student[1], student[2], "student")
        
        teacher = self.get_teacher_by_email(email)
        if teacher:
            # Retorna (nome, email, tipo_utilizador)
            return (teacher[1], teacher[2], "teacher")

        return None