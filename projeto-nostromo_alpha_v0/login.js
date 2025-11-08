document.addEventListener("DOMContentLoaded", () => {
    const loginForm = document.getElementById("login-form");
    const loginMessage = document.getElementById("login-message");
    const loginButton = loginForm.querySelector("button");

    if (loginForm) {
        loginForm.addEventListener("submit", async (e) => {
            e.preventDefault(); // Impedir o envio padrão do formulário

            // Pegar os valores dos campos
            const email = document.getElementById("login-email").value;
            const password = document.getElementById("login-password").value;

            // Mostrar feedback de carregamento
            loginButton.disabled = true;
            loginButton.textContent = "Entrando...";
            loginMessage.textContent = "";
            loginMessage.className = "";

            try {
                // MUDANÇA: Apontar para a nova rota da API com prefixo /api
                const response = await fetch('/api/login', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        email: email,
                        password: password
                    }),
                    // 'credentials: "include"' é vital para enviar/receber cookies HttpOnly
                    credentials: "include" 
                });

                // O servidor agora define o cookie HttpOnly automaticamente

                if (response.ok) { // Status 200-299
                    // Não precisamos guardar nada no localStorage
                    // O cookie está seguro no navegador
                    
                    // Mostrar sucesso e redirecionar
                    loginMessage.textContent = "Login bem-sucedido! A redirecionar...";
                    loginMessage.className = "success";
                    
                    // Redirecionar para a página principal
                    window.location.href = "/main.html";

                } else {
                    // Tratar erros (ex: 401 Senha inválida)
                    const errorData = await response.json();
                    loginMessage.textContent = errorData.error || "Email ou senha inválidos";
                    loginMessage.className = "error";
                    loginButton.disabled = false;
                    loginButton.textContent = "Entrar";
                }
            } catch (error) {
                // Tratar erros de rede (ex: servidor offline)
                console.error("Erro na requisição:", error);
                loginMessage.textContent = "Erro de conexão. Tente novamente.";
                loginMessage.className = "error";
                loginButton.disabled = false;
                loginButton.textContent = "Entrar";
            }
        });
    }
});