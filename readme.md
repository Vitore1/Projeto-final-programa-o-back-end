Sistema de gerenciamento de chamados técnicos desenvolvido em Python com Flask e MySQL. Permite o cadastro de setores, usuários e o gerenciamento completo de chamados técnicos.

## ✨ Funcionalidades

### 📋 Backend (API REST)
- **CRUD completo** de Setores, Usuários e Chamados
- **Validações robustas** de dados e integridade referencial
- **Status automático** - Chamados criados com status "aberto"
- **Prioridades** - Baixa, Média e Alta com ordenação automática
- **Relacionamentos** - Usuários pertencem a setores, chamados vinculados a ambos
- **Health Check** - Rota `/health` para monitoramento
- **Configuração por ambiente** - Variáveis `.env` para segurança

### 🖥️ Frontend (CLI Interativo)
- **Menu intuitivo** - Interface amigável em terminal
- **Tratamento de erros** - Conexão com API, timeouts, validações
- **Visualização rica** - Emojis, cores e formatação organizada
- **Validações** - Confirmações para ações destrutivas
- **Dados de demonstração** - Opção para carregar dados de teste

### 🗄️ Banco de Dados
- **Modelo relacional correto** - Chaves estrangeiras e integridade
- **Auto-inicialização** - Banco e tabelas criados automaticamente
- **Enums** - Status e prioridades com valores controlados
- **Índices** - Otimização para consultas frequentes

## Arquitetura
service_desk/
├── app.py # Backend Flask (API REST)
├── config.py # Configurações da aplicação
├── menu.py # Cliente CLI interativo
├── requirements.txt # Dependências do projeto
├── .env # Variáveis de ambiente (não versionar)
├── .env.example # Template das variáveis (versionar)
└── README.md # Esta documentação


## Instalação Rápida

### 1. Pré-requisitos
- Python 3.8 ou superior
- MySQL 8.0 ou superior
- pip (gerenciador de pacotes Python)

### 2. Clonar e Configurar
```bash
# Clone o repositório (se for o caso)
# git clone <url-do-repositorio>
# cd service_desk

# Crie um ambiente virtual (recomendado)
python -m venv venv

# Ative o ambiente virtual
# Windows:
venv\Scripts\activate

# Linux/Mac:
source venv/bin/activate

# Instale as dependências
pip install -r requirements.txt

### 3. Configuração de Banco de dados
# 1. Instale o MySQL se não tiver
# 2. Crie um arquivo .env

### 4. Configurar o arquivo .env

# Banco de Dados MySQL
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=sua_senha_aqui
MYSQL_DB=service_desk
MYSQL_PORT=3306

# Configurações da Aplicação
DEBUG=True
SECRET_KEY=chave_secreta_para_producao_mude_isso

### 5. Executar o Sistema

# Terminal 1 - Iniciar o servidor backend
python app.py

# Terminal 2 - Iniciar o cliente (em outro terminal)
python menu.py

### 6. Endpoints da API

#Saúde do Sistema
GET / - Página inicial com informações
GET /health - Verifica saúde da API e banco

#Setores
GET /setor - Lista todos os setores
POST /setor - Cria um novo setor

#Usuários
GET /usuario - Lista todos os usuários (com setor)
POST /usuario - Cria um novo usuário

#Chamados
GET /chamados - Lista todos os chamados (com usuário e setor)
POST /chamados - Abre um novo chamado
PUT /chamados/<id> - Atualiza status/prioridade
DELETE /chamados/<id> - Remove um chamado

### 7.Como Usar o Sistema
Fluxo Básico:
1.Inicie o servidor: python app.py

2.Inicie o cliente: python menu.py

3.Crie um setor: Opção 2 no menu

4.Crie um usuário: Opção 4 (vinculado a um setor)

5.Abra um chamado: Opção 6

6.Gerencie chamados: Liste, atualize status, delete

### 8. Estrutura do Banco de Dados

#Tabela setor
sql
id_setor INT AUTO_INCREMENT PRIMARY KEY
nome VARCHAR(100) NOT NULL
#Tabela usuario
sql
id_usuario INT AUTO_INCREMENT PRIMARY KEY
nome VARCHAR(100) NOT NULL
email VARCHAR(100) UNIQUE NOT NULL
setor_id INT NOT NULL FOREIGN KEY REFERENCES setor(id_setor)
#Tabela chamados
sql
id_chamado INT AUTO_INCREMENT PRIMARY KEY
titulo VARCHAR(100) NOT NULL
descricao TEXT
prioridade ENUM('baixa','media','alta') NOT NULL
status ENUM('aberto','em atendimento','concluido') DEFAULT 'aberto'
data_abertura TIMESTAMP DEFAULT CURRENT_TIMESTAMP
usuario_id INT NOT NULL FOREIGN KEY REFERENCES usuario(id_usuario)
setor_id INT NOT NULL FOREIGN KEY REFERENCES setor(id_setor)
