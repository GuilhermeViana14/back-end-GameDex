from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# URL de conexão com o banco padrão (postgres)
DATABASE_URL = "postgresql://postgres:123@localhost/gamedex?client_encoding=utf8"
TARGET_DATABASE = "gamedex"  # Nome do banco de dados que será criado

# Configuração do SQLAlchemy para o banco padrão
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Função para criar o banco de dados, se não existir
def create_database():
    with engine.connect() as connection:
        result = connection.execute(
            text(f"SELECT 1 FROM pg_database WHERE datname = '{TARGET_DATABASE}'")
        )
        if not result.fetchone():
            connection.execute(text(f"CREATE DATABASE {TARGET_DATABASE} ENCODING 'UTF8'"))
            print(f"Banco de dados '{TARGET_DATABASE}' criado com sucesso!")
        else:
            print(f"Banco de dados '{TARGET_DATABASE}' já existe.")

# Dependência para obter a sessão do banco de dados
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()