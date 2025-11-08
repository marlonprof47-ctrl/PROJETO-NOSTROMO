import os
import bcrypt
import jwt
import datetime
from functools import wraps
from dotenv import load_dotenv
from flask import Flask, request, jsonify, make_response, send_from_directory
from werkzeug.utils import safe_join

# Opcional: habilitar CORS só se necessário
FRONTEND_ORIGIN = os.getenv("FRONTEND_ORIGIN")  # ex: "http://127.0.0.1:5500"
# Se FRONTEND_ORIGIN estiver definido, assumimos front e back em origens diferentes.

# Carregar variáveis de ambiente (SECRET_KEY) do ficheiro .env
load_dotenv()

# Importar os nossos módulos locais
from data_warehouse.db_manager import DBManager
from login_system.validators import validate_password, validate_ra, validate_registration_number

# --- CONFIGURAÇÃO DA APLICAÇÃO ---
STATIC_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'projeto-nostromo_alpha_v0'))
app = Flask(__name__, static_folder=STATIC_FOLDER, static_url_path='')


# Se deseja usar CORS cross-origin, activa-se só quando FRONTEND_ORIGIN está definido
if FRONTEND_ORIGIN:
    try:
        from flask_cors import CORS
        # Permitir credenciais (cookies) vindos do front-end
        CORS(app, supports_credentials=True, origins=[FRONTEND_ORIGIN])
        print(f"Aviso: CORS cross-origin activo para {FRONTEND_ORIGIN}")
    except Exception:
        # flask_cors pode não estar instalado
        print("Aviso: flask_cors não encontrado. Instale com: pip install flask-cors se usar FRONTEND_ORIGIN.")

# Obter a chave secreta do ambiente
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("Nenhuma SECRET_KEY definida nas variáveis de ambiente. Crie um ficheiro .env.")

db = DBManager()

print(f"Servidor Flask (com JWT e bcrypt) a iniciar...")
print(f"A servir arquivos estáticos de: {STATIC_FOLDER}")
if FRONTEND_ORIGIN:
    print(f"Front-end em origem diferente: {FRONTEND_ORIGIN} -> CORS com credenciais activo")
else:
    print("Front-end servido pela mesma origem (recomendada para dev).")

# --- DECORATOR DE AUTENTICAÇÃO ---
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.cookies.get('token')
        if not token:
            return jsonify({"error": "Token em falta"}), 401
        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            current_user_email = data['email']
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token expirado"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Token inválido"}), 401
        return f(current_user_email=current_user_email, *args, **kwargs)
    return decorated

# --- HELPER PARA CRIAR O COOKIE ---
def create_session_cookie(email: str, user_type: str, status_code: int = 200):
    """Cria JWT e retorna response com Set-Cookie apropriado."""
    try:
        # Expiração em UTC
        exp = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=24)
        token = jwt.encode({
            'email': email,
            'user_type': user_type,
            'exp': exp
        }, SECRET_KEY, algorithm="HS256")

        # jwt.encode pode retornar bytes em algumas versões
        if isinstance(token, bytes):
            token = token.decode('utf-8')

        response = make_response(jsonify({"message": "Autenticação bem-sucedida"}), status_code)

        # Escolher samesite/secure dependendo se o front está em origem diferente
        if FRONTEND_ORIGIN:
            # Cross-site: requer SameSite=None e Secure=True (HTTPS necessário)
            cookie_kwargs = {
                'httponly': True,
                'secure': True,           # Requer HTTPS (produção / dev com HTTPS)
                'samesite': 'None',
                'expires': exp,
                'path': '/'
            }
        else:
            # Mesma origem (dev simples): Lax funciona e permite POST/XHR no mesmo host
            cookie_kwargs = {
                'httponly': True,
                'secure': False,          # Em dev HTTP local
                'samesite': 'Lax',
                'expires': exp,
                'path': '/'
            }

        response.set_cookie('token', token, **cookie_kwargs)

        return response
    except Exception as e:
        return make_response(jsonify({"error": f"Erro ao criar sessão: {str(e)}"}), 500)


# --- ROTAS DE API ---
@app.route('/api/register/student', methods=['POST'])
def api_register_student():
    data = request.json
    if not data:
        return jsonify({"error": "Nenhum dado enviado"}), 400
    name = data.get('name'); email = data.get('email'); password = data.get('password')
    ra = data.get('ra'); course = data.get('course'); period = data.get('period')
    agreed_eula = data.get('agreed_eula')

    if not password or not validate_password(password):
        return jsonify({"error": "Senha inválida"}), 400
    if not ra or not validate_ra(ra):
        return jsonify({"error": "RA inválido"}), 400
    if not agreed_eula:
        return jsonify({"error": "Você deve aceitar a EULA"}), 400

    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password_bytes, salt)

    student_data = {
        "name": name, "email": email,
        "password": hashed_password.decode('utf-8'),
        "ra": ra, "course": course, "period": period,
        "agreed_eula": agreed_eula, "passed_captcha": True
    }

    try:
        success = db.insert_student(student_data)
        if success:
            return create_session_cookie(email, "student", status_code=201)
        else:
            return jsonify({"error": "Email ou RA já existe"}), 409
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/register/teacher', methods=['POST'])
def api_register_teacher():
    data = request.json
    if not data:
        return jsonify({"error": "Nenhum dado enviado"}), 400
    name = data.get('name'); email = data.get('email'); password = data.get('password')
    registration_number = data.get('registration_number'); agreed_eula = data.get('agreed_eula')

    if not validate_password(password):
        return jsonify({"error": "Senha inválida"}), 400
    if not validate_registration_number(registration_number):
        return jsonify({"error": "Número de registro inválido"}), 400
    if not agreed_eula:
        return jsonify({"error": "Você deve aceitar o EULA"}), 400

    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password_bytes, salt)

    teacher_data = {
        "name": name, "email": email,
        "password": hashed_password.decode('utf-8'),
        "registration_number": registration_number,
        "agreed_eula": agreed_eula, "passed_captcha": True
    }

    try:
        success = db.insert_teacher(teacher_data)
        if success:
            return create_session_cookie(email, "teacher", status_code=201)
        else:
            return jsonify({"error": "Email ou número de registro já existe"}), 409
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.json
    email = data.get('email'); password = data.get('password')

    if not email or not password:
        return jsonify({"error": "Email e senha são obrigatórios"}), 400

    user_type = None; stored_hash = None

    student = db.get_student_by_email(email)
    if student:
        user_type = "student"; stored_hash = student[3]

    if not student:
        teacher = db.get_teacher_by_email(email)
        if teacher:
            user_type = "teacher"; stored_hash = teacher[3]

    if user_type and stored_hash:
        password_bytes = password.encode('utf-8'); stored_hash_bytes = stored_hash.encode('utf-8')
        if bcrypt.checkpw(password_bytes, stored_hash_bytes):
            return create_session_cookie(email, user_type)

    return jsonify({"error": "Email ou senha inválidos"}), 401

# --- ROTAS PRIVADAS ---
@app.route('/api/profile', methods=['GET'])
@token_required
def get_profile(current_user_email):
    user_data = db.get_user_by_email(current_user_email)
    if user_data:
        profile_info = {"name": user_data[0], "email": user_data[1], "user_type": user_data[2]}
        return jsonify(profile_info), 200
    else:
        return jsonify({"error": "Utilizador não encontrado"}), 404

# ==========================================================
# --- ROTA DE NOTAS ATUALIZADA ---
# ==========================================================
@app.route('/api/grades', methods=['GET'])
@token_required
def get_grades(current_user_email):
    # O decorator @token_required garante que só utilizadores logados cheguem aqui.
    
    # MUDANÇA: Substituímos os dados antigos pelos dados que você pediu.
    mock_grades = [
        { "disciplina": "Programação para Banco de Dados", "p1": 8.5, "p2": 9.0, "media": 8.8, "status": "Aprovado" },
        { "disciplina": "Métodos Matemáticos", "p1": 6.0, "p2": 7.0, "media": 6.5, "status": "Aprovado" },
        { "disciplina": "Física Geral", "p1": 3.0, "p2": 4.0, "media": 3.5, "status": "Reprovado" },
        { "disciplina": "Desenvolvimento Low Code", "p1": 9.0, "p2": 10.0, "media": 9.5, "status": "Aprovado" },
        { "disciplina": "Ecommerce com CMS", "p1": 7.0, "p2": 0.0, "media": 3.5, "status": "Cursando" }
    ]
    
    return jsonify(mock_grades), 200
# ==========================================================


@app.route('/api/logout', methods=['POST'])
def api_logout():
    response = make_response(jsonify({"message": "Logout bem-sucedido"}), 200)
    # Remover cookie no path raiz: definir max_age=0 e path='/'
    cookie_kwargs = {
        'httponly': True,
        'expires': 0,
        'max_age': 0,
        'path': '/',
        'samesite': 'Lax',
        'secure': False
    }
    if FRONTEND_ORIGIN:
        cookie_kwargs['samesite'] = 'None'
        cookie_kwargs['secure'] = True
        
    response.set_cookie('token', '', **cookie_kwargs)
    return response

@app.route('/api/delete-account', methods=['DELETE'])
@token_required
def delete_account(current_user_email):
    user_data = db.get_user_by_email(current_user_email)
    if not user_data:
        return jsonify({"error": "Utilizador não encontrado"}), 404

    user_type = user_data[2]
    success = False
    try:
        if user_type == 'student':
            success = db.delete_student_by_email(current_user_email)
        elif user_type == 'teacher':
            success = db.delete_teacher_by_email(current_user_email)
        
        if success:
            response = make_response(jsonify({"message": "Conta excluída com sucesso"}), 200)
            # Definir opções de cookie para logout
            cookie_kwargs = {
                'httponly': True,
                'expires': 0,
                'max_age': 0,
                'path': '/',
                'samesite': 'Lax',
                'secure': False
            }
            if FRONTEND_ORIGIN:
                cookie_kwargs['samesite'] = 'None'
                cookie_kwargs['secure'] = True
            
            response.set_cookie('token', '', **cookie_kwargs)
            return response
        else:
            return jsonify({"error": "Falha ao excluir a conta"}), 500
    except Exception as e:
        return jsonify({"error": f"Erro interno: {str(e)}"}), 500

# --- ROTAS DE FRONT-END ---
@app.route('/')
def serve_index():
    return send_from_directory(STATIC_FOLDER, 'index.html')

@app.route('/<path:page_name>')
def serve_html_page(page_name):
    # Esta rota "apanha-tudo" serve:
    # 1. Páginas HTML (ex: /main.html, /perfil.html)
    # 2. Arquivos CSS (ex: /main.css, /perfil.css)
    # 3. Arquivos JS (ex: /login.js, /cadastro.js)
    
    # Tenta encontrar o arquivo solicitado
    safe_path = safe_join(STATIC_FOLDER, page_name)
    
    # Verifica se o caminho é seguro e se o arquivo existe
    if os.path.normpath(safe_path).startswith(STATIC_FOLDER) and os.path.isfile(safe_path):
        return send_from_directory(STATIC_FOLDER, page_name)
    else:
        # Se não encontrar (ex: /paginaquenaoexiste ou /api/...), 
        # e não for uma rota de API, serve o index.
        # As rotas de API (ex: /api/login) são tratadas antes disto.
        # Se chegar aqui e não for um arquivo, é provável que seja um 404
        # mas redirecionar para o index é mais seguro para SPAs
        return send_from_directory(STATIC_FOLDER, 'index.html')

# --- Rodar o Servidor ---
if __name__ == "__main__":
    app.run(debug=True, port=5000, host='0.0.0.0')