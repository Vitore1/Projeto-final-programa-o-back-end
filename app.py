# Projeto final do curso de backend senai versao 3 "frankenstein"
from flask import Flask, jsonify, request
import mysql.connector
from mysql.connector import Error, IntegrityError
from app_config import Config

app = Flask(__name__)
app.config.from_object(Config)

# Constantes para validação
STATUS_VALIDOS = ['aberto', 'em atendimento', 'concluido', 'cancelado']
PRIORIDADES_VALIDAS = ['critica', 'alta', 'media', 'baixa']

def get_db_connection():
    """Cria conexão com o banco de dados"""
    try:
        connection = mysql.connector.connect(
            host=app.config['MYSQL_HOST'],
            user=app.config['MYSQL_USER'],
            password=app.config['MYSQL_PASSWORD'],
            database=app.config['MYSQL_DB'],
            port=app.config['MYSQL_PORT']
        )
        if connection.is_connected():
            return connection
    except Error as e:
        print(f"Erro ao conectar ao MySQL: {e}")
        return None
    return None

def init_db():
    """Cria banco e tabelas se não existirem"""
    print("🔄 Inicializando banco de dados...")
    
    try:
        # Conecta sem database primeiro
        connection = mysql.connector.connect(
            host=app.config['MYSQL_HOST'],
            user=app.config['MYSQL_USER'],
            password=app.config['MYSQL_PASSWORD'],
            port=app.config['MYSQL_PORT']
        )
        cursor = connection.cursor()
        
        # Cria database
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {app.config['MYSQL_DB']}")
        cursor.execute(f"USE {app.config['MYSQL_DB']}")
        
        # Cria tabela de setores
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS setor (
                id_setor INT AUTO_INCREMENT PRIMARY KEY,
                nome VARCHAR(100) NOT NULL
            )
        """)
        
        # Cria tabela de usuários
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS usuario (
                id_usuario INT AUTO_INCREMENT PRIMARY KEY,
                nome VARCHAR(100) NOT NULL,
                email VARCHAR(100) NOT NULL UNIQUE,
                setor_id INT NOT NULL,
                FOREIGN KEY (setor_id) REFERENCES setor(id_setor) 
                ON DELETE RESTRICT ON UPDATE CASCADE
            )
        """)
        
        # Cria tabela de chamados
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chamados (
                id_chamado INT AUTO_INCREMENT PRIMARY KEY,
                titulo VARCHAR(100) NOT NULL,
                descricao TEXT,
                prioridade ENUM('baixa','media','alta') NOT NULL,
                status ENUM('aberto','em atendimento','concluido') NOT NULL DEFAULT 'aberto',
                data_abertura TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                usuario_id INT NOT NULL,
                setor_id INT NOT NULL,
                FOREIGN KEY (usuario_id) REFERENCES usuario(id_usuario) 
                ON DELETE RESTRICT ON UPDATE CASCADE,
                FOREIGN KEY (setor_id) REFERENCES setor(id_setor) 
                ON DELETE RESTRICT ON UPDATE CASCADE
            )
        """)
        
        connection.commit()
        print("Banco de dados inicializado com sucesso!")
        
    except Error as e:
        print(f"Erro na inicialização: {e}")
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'connection' in locals() and connection:
            connection.close()

# ==================== FUNÇÕES AUXILIARES ====================
def setor_existe(setor_id):
    conexao = get_db_connection()
    if not conexao:
        return False
    try:
        cursor = conexao.cursor()
        cursor.execute("SELECT 1 FROM setor WHERE id_setor = %s", (setor_id,))
        return cursor.fetchone() is not None
    finally:
        cursor.close()
        conexao.close()

def usuario_existe(usuario_id):
    conexao = get_db_connection()
    if not conexao:
        return False
    try:
        cursor = conexao.cursor()
        cursor.execute("SELECT 1 FROM usuario WHERE id_usuario = %s", (usuario_id,))
        return cursor.fetchone() is not None
    finally:
        cursor.close()
        conexao.close()

def chamado_existe(chamado_id):
    conexao = get_db_connection()
    if not conexao:
        return False
    try:
        cursor = conexao.cursor()
        cursor.execute("SELECT 1 FROM chamados WHERE id_chamado = %s", (chamado_id,))
        return cursor.fetchone() is not None
    finally:
        cursor.close()
        conexao.close()

# ==================== ROTAS DA API ====================
@app.route('/')
def home():
    return jsonify({
        "mensagem": "API Service Desk - Sistema de Chamados Técnicos",
        "status": "online",
        "versao": "2.0",
        "endpoints": {
            "setores": "/setor",
            "usuarios": "/usuario", 
            "chamados": "/chamados",
            "saude": "/health"
        }
    })
#================== health check (get)====================
@app.route('/health', methods=['GET'])
def health_check():
    """Verificar saúde da API e do banco"""
    try:
        conexao = get_db_connection()
        if conexao and conexao.is_connected():
            return jsonify({
                "status": "online",
                "database": "connected",
                "config": {
                    "host": app.config['MYSQL_HOST'],
                    "database": app.config['MYSQL_DB']
                }
            }), 200
        else:
            return jsonify({
                "status": "online",
                "database": "disconnected"
            }), 503
    except Exception as e:
        return jsonify({"status": "error", "erro": str(e)}), 500

# ================== criar setor(post) =======================
@app.route('/setor', methods=['POST'])
def criar_setor():
    dados = request.json
    
    if not dados or 'nome' not in dados:
        return jsonify({"erro": "Campo 'nome' é obrigatório"}), 400
    
    conexao = get_db_connection()
    if not conexao:
        return jsonify({"erro": "Falha na conexão com o banco"}), 500
    
    cursor = None
    try:
        cursor = conexao.cursor()
        sql = "INSERT INTO setor (nome) VALUES (%s)"
        cursor.execute(sql, (dados['nome'],))
        conexao.commit()
        
        return jsonify({
            "mensagem": "Setor criado com sucesso",
            "id_setor": cursor.lastrowid
        }), 201
        
    except Error as e:
        return jsonify({"erro": f"Erro no banco: {str(e)}"}), 500
    finally:
        if cursor:
            cursor.close()
        if conexao:
            conexao.close()
#==================== listar setor(get)===============
@app.route('/setor', methods=['GET'])
def listar_setores():
    conexao = get_db_connection()
    if not conexao:
        return jsonify({"erro": "Falha na conexão"}), 500
    
    cursor = None
    try:
        cursor = conexao.cursor(dictionary=True)
        cursor.execute("SELECT * FROM setor ORDER BY nome")
        setores = cursor.fetchall()
        return jsonify(setores), 200
    except Error as e:
        return jsonify({"erro": str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conexao:
            conexao.close()

# ========================= criar usuario (post)===============
@app.route('/usuario', methods=['POST'])
def criar_usuario():
    dados = request.json
    
    if not dados or 'nome' not in dados or 'email' not in dados or 'setor_id' not in dados:
        return jsonify({
            "erro": "Campos obrigatórios: nome, email, setor_id"
        }), 400
    
    if not setor_existe(dados['setor_id']):
        return jsonify({"erro": "Setor informado não existe"}), 404
    
    conexao = get_db_connection()
    if not conexao:
        return jsonify({"erro": "Falha na conexão"}), 500
    
    cursor = None
    try:
        cursor = conexao.cursor()
        sql = """
            INSERT INTO usuario (nome, email, setor_id)
            VALUES (%s, %s, %s)
        """
        cursor.execute(sql, (
            dados['nome'],
            dados['email'],
            dados['setor_id']
        ))
        conexao.commit()
        
        return jsonify({
            "mensagem": "Usuário criado com sucesso",
            "id_usuario": cursor.lastrowid
        }), 201
        
    except IntegrityError:
        return jsonify({"erro": "Email já cadastrado"}), 409
    except Error as e:
        return jsonify({"erro": f"Erro no banco: {str(e)}"}), 500
    finally:
        if cursor:
            cursor.close()
        if conexao:
            conexao.close()
# ====================== listar usuario(get) ========================
@app.route('/usuario', methods=['GET'])
def listar_usuarios():
    conexao = get_db_connection()
    if not conexao:
        return jsonify({"erro": "Falha na conexão"}), 500
    
    cursor = None
    try:
        cursor = conexao.cursor(dictionary=True)
        sql = """
            SELECT 
                u.id_usuario,
                u.nome,
                u.email,
                s.nome AS setor,
                u.setor_id
            FROM usuario u
            JOIN setor s ON u.setor_id = s.id_setor
            ORDER BY u.nome
        """
        cursor.execute(sql)
        usuarios = cursor.fetchall()
        return jsonify(usuarios), 200
    except Error as e:
        return jsonify({"erro": str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conexao:
            conexao.close()

# ===================== criar chamados(post) ==================
@app.route('/chamados', methods=['POST'])
def criar_chamado():
    dados = request.json
    
    campos_obrigatorios = ['titulo', 'descricao', 'prioridade', 'usuario_id', 'setor_id']
    
    for campo in campos_obrigatorios:
        if campo not in dados or not dados[campo]:
            return jsonify({"erro": f"Campo '{campo}' é obrigatório"}), 400
    
    prioridade = dados['prioridade'].strip().lower()
    if prioridade not in PRIORIDADES_VALIDAS:
        return jsonify({
            "erro": "Prioridade inválida",
            "valores_permitidos": PRIORIDADES_VALIDAS
        }), 400
    
    if not usuario_existe(dados['usuario_id']):
        return jsonify({"erro": "Usuário não encontrado"}), 404
    
    if not setor_existe(dados['setor_id']):
        return jsonify({"erro": "Setor não encontrado"}), 404
    
    conexao = get_db_connection()
    if not conexao:
        return jsonify({"erro": "Falha na conexão"}), 500
    
    cursor = None
    try:
        cursor = conexao.cursor()
        sql = """
            INSERT INTO chamados 
            (titulo, descricao, prioridade, status, usuario_id, setor_id)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        
        cursor.execute(sql, (
            dados['titulo'],
            dados['descricao'],
            prioridade,
            'aberto',
            dados['usuario_id'],
            dados['setor_id']
        ))
        
        conexao.commit()
        
        return jsonify({
            "mensagem": "Chamado criado com sucesso",
            "id_chamado": cursor.lastrowid,
            "status_inicial": "aberto"
        }), 201
        
    except Error as e:
        return jsonify({"erro": f"Erro no banco: {str(e)}"}), 500
    finally:
        if cursor:
            cursor.close()
        if conexao:
            conexao.close()
#==================== listar chamados(get)===================
@app.route('/chamados', methods=['GET'])
def listar_chamados():
    conexao = get_db_connection()
    if not conexao:
        return jsonify({"erro": "Falha na conexão"}), 500
    
    cursor = None
    try:
        cursor = conexao.cursor(dictionary=True)
        sql = """
            SELECT 
                c.id_chamado,
                c.titulo,
                c.descricao,
                c.prioridade,
                c.status,
                c.data_abertura,
                u.nome AS usuario,
                s.nome AS setor,
                u.id_usuario,
                s.id_setor
            FROM chamados c
            JOIN usuario u ON c.usuario_id = u.id_usuario
            JOIN setor s ON c.setor_id = s.id_setor
            ORDER BY 
                CASE c.prioridade
                    WHEN 'alta' THEN 1
                    WHEN 'media' THEN 2
                    WHEN 'baixa' THEN 3
                END,
                c.data_abertura DESC
        """
        cursor.execute(sql)
        chamados = cursor.fetchall()
        return jsonify(chamados), 200
    except Error as e:
        return jsonify({"erro": str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conexao:
            conexao.close()
#======================== atualizar chamados(put) =================
@app.route('/chamados/<int:chamado_id>', methods=['PUT'])
def atualizar_chamado(chamado_id):
    if not chamado_existe(chamado_id):
        return jsonify({"erro": "Chamado não encontrado"}), 404
    
    dados = request.json
    if not dados:
        return jsonify({"erro": "Nenhum dado enviado"}), 400
    
    if 'status' in dados and dados['status'] not in STATUS_VALIDOS:
        return jsonify({
            "erro": "Status inválido",
            "valores_permitidos": STATUS_VALIDOS
        }), 400
    
    if 'prioridade' in dados and dados['prioridade'] not in PRIORIDADES_VALIDAS:
        return jsonify({
            "erro": "Prioridade inválida",
            "valores_permitidos": PRIORIDADES_VALIDAS
        }), 400
    
    campos = []
    valores = []
    
    if 'status' in dados:
        campos.append("status = %s")
        valores.append(dados['status'].strip().lower())
    if 'prioridade' in dados:
        campos.append("prioridade = %s")
        valores.append(dados['prioridade'].strip().lower())
    
    if not campos:
        return jsonify({"erro": "Nenhum campo válido para atualizar"}), 400
    
    valores.append(chamado_id)
    
    conexao = get_db_connection()
    if not conexao:
        return jsonify({"erro": "Falha na conexão"}), 500
    
    cursor = None
    try:
        cursor = conexao.cursor()
        query = f"UPDATE chamados SET {', '.join(campos)} WHERE id_chamado = %s"
        cursor.execute(query, tuple(valores))
        conexao.commit()
        
        if cursor.rowcount == 0:
            return jsonify({"erro": "Chamado não encontrado"}), 404
        
        return jsonify({
            "mensagem": "Chamado atualizado com sucesso",
            "campos_atualizados": [campo.replace(" = %s", "") for campo in campos]
        }), 200
        
    except Error as e:
        return jsonify({"erro": f"Erro no banco: {str(e)}"}), 500
    finally:
        if cursor:
            cursor.close()
        if conexao:
            conexao.close()
#================== deletar chamados (delete)=================
@app.route('/chamados/<int:chamado_id>', methods=['DELETE'])
def deletar_chamado(chamado_id):
    if not chamado_existe(chamado_id):
        return jsonify({"erro": "Chamado não encontrado"}), 404
    
    conexao = get_db_connection()
    if not conexao:
        return jsonify({"erro": "Falha na conexão"}), 500
    
    cursor = None
    try:
        cursor = conexao.cursor()
        cursor.execute("DELETE FROM chamados WHERE id_chamado = %s", (chamado_id,))
        conexao.commit()
        
        if cursor.rowcount == 0:
            return jsonify({"erro": "Chamado não encontrado"}), 404
        
        return jsonify({"mensagem": "Chamado deletado com sucesso"}), 200
    except Error as e:
        return jsonify({"erro": f"Erro no banco: {str(e)}"}), 500
    finally:
        if cursor:
            cursor.close()
        if conexao:
            conexao.close()

# ==================== INICIALIZAÇÃO (smp no final""""") ====================
if __name__ == '__main__':
    init_db()
    print(f"🚀 Servidor iniciando em: http://{app.config['MYSQL_HOST']}:5000")
    print(f"📊 Banco de dados: {app.config['MYSQL_DB']}")
    app.run(
        debug=app.config['DEBUG'],
        host='0.0.0.0',
        port=5000,
        use_reloader=False
    )

    #está vivo!!!!!!!!!!!