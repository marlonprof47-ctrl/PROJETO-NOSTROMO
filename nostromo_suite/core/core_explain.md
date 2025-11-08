# 📘 /core — Módulo Central do Nostromo Suite

O diretório **/core** contém os componentes fundamentais do sistema:

| Arquivo | Função |
|----------|--------|
| `config.py` | Configurações globais e caminhos padrão |
| `db_manager.py` | Inicialização e controle do banco SQLite |
| `security.py` | Hash de senhas e autenticação básica |
| `logger.py` | Registro de eventos do sistema |
| `utils.py` | Funções auxiliares diversas |
| `__init__.py` | Indica que o diretório é um módulo Python |

Tudo o que está aqui **pode ser importado por qualquer outro módulo**, mas o `/core` **nunca deve depender de módulos externos**.