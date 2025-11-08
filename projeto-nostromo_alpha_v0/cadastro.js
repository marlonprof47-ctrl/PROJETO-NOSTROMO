document.addEventListener("DOMContentLoaded", () => {
    const radioAluno = document.getElementById("radio-aluno");
    const radioProfessor = document.getElementById("radio-professor");
    const formAluno = document.getElementById("form-aluno");
    const formProfessor = document.getElementById("form-professor");
    const registerMessage = document.getElementById("register-message");

    // Lógica para alternar formulários
    radioAluno.addEventListener("change", () => {
        if (radioAluno.checked) {
            formAluno.style.display = "block";
            formProfessor.style.display = "none";
            registerMessage.textContent = ""; // Limpar mensagens
        }
    });

    radioProfessor.addEventListener("change", () => {
        if (radioProfessor.checked) {
            formAluno.style.display = "none";
            formProfessor.style.display = "block";
            registerMessage.textContent = ""; // Limpar mensagens
        }
    });

    // Função genérica de envio de formulário
    const handleRegisterSubmit = async (form, apiUrl, payload) => {
        const submitButton = form.querySelector("button[type='submit']");
        
        // Feedback de carregamento
        submitButton.disabled = true;
        submitButton.textContent = "Cadastrando...";
        registerMessage.textContent = "";
        registerMessage.className = "";

        try {
            const response = await fetch(apiUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(payload),
                 // 'credentials: "include"' é vital para enviar/receber cookies HttpOnly
                credentials: "include"
            });
            
            // O servidor define o cookie HttpOnly automaticamente

            if (response.ok) { // Status 201 Created
                // Não guardamos nada no localStorage
                // O cookie está seguro no navegador

                // Mostrar sucesso e redirecionar
                registerMessage.textContent = "Cadastro bem-sucedido! A redirecionar...";
                registerMessage.className = "success";
                
                // Redirecionar para a página principal
                window.location.href = "/main.html";

            } else {
                // Tratar erros (ex: 409 Email já existe)
                const errorData = await response.json();
                registerMessage.textContent = errorData.error || "Erro ao cadastrar. Verifique os dados.";
                registerMessage.className = "error";
                submitButton.disabled = false;
                submitButton.textContent = "Cadastrar";
            }
        } catch (error) {
            // Tratar erros de rede (ex: servidor offline)
            console.error("Erro na requisição:", error);
            registerMessage.textContent = "Erro de conexão. Tente novamente.";
            registerMessage.className = "error";
            submitButton.disabled = false;
            submitButton.textContent = "Cadastrar";
        }
    };

    // Listener para o formulário de Aluno
    formAluno.addEventListener("submit", (e) => {
        e.preventDefault();
        const pass1 = document.getElementById("reg-aluno-pass1").value;
        const pass2 = document.getElementById("reg-aluno-pass2").value;

        if (pass1 !== pass2) {
            registerMessage.textContent = "As senhas não coincidem.";
            registerMessage.className = "error";
            return;
        }

        const payload = {
            name: document.getElementById("reg-aluno-name").value,
            email: document.getElementById("reg-aluno-email").value,
            period: document.getElementById("reg-aluno-periodo").value,
            password: pass1,
            ra: document.getElementById("reg-aluno-ra").value,
            course: document.getElementById("reg-aluno-curso").value,
            agreed_eula: document.getElementById("reg-aluno-eula").checked,
        };
        
        // MUDANÇA: Apontar para a nova rota com /api
        handleRegisterSubmit(formAluno, '/api/register/student', payload);
    });

    // Listener para o formulário de Professor
    formProfessor.addEventListener("submit", (e) => {
        e.preventDefault();
        const pass1 = document.getElementById("reg-prof-pass1").value;
        const pass2 = document.getElementById("reg-prof-pass2").value;

        if (pass1 !== pass2) {
            registerMessage.textContent = "As senhas não coincidem.";
            registerMessage.className = "error";
            return;
        }

        const payload = {
            name: document.getElementById("reg-prof-name").value,
            email: document.getElementById("reg-prof-email").value,
            password: pass1,
            registration_number: document.getElementById("reg-prof-reg").value,
            agreed_eula: document.getElementById("reg-prof-eula").checked,
        };
        
        // MUDANÇA: Apontar para a nova rota com /api
        handleRegisterSubmit(formProfessor, '/api/register/teacher', payload);
    });
});