import os
from dotenv import load_dotenv

# Carrega variáveis do .env
load_dotenv()

class Config:
    """Configurações da aplicação Service Desk"""
    
    # Banco de dados MySQL
    MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
    MYSQL_USER = os.getenv("MYSQL_USER", "root")
    MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "Vitor123!")
    MYSQL_DB = os.getenv("MYSQL_DB", "service_desk")
    MYSQL_PORT = int(os.getenv("MYSQL_PORT", "3306"))
    
    # Configurações da aplicação
    DEBUG = os.getenv("DEBUG", "True").lower() == "true"
    SECRET_KEY = os.getenv("SECRET_KEY", "chave_secreta_padrao_para_desenvolvimento")
    
    # Configurações da API
    API_HOST = os.getenv("API_HOST", "0.0.0.0")
    API_PORT = int(os.getenv("API_PORT", "5000"))