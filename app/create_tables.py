from sqlalchemy import create_engine
from app.database import Base, create_database
from app.models.User import User

# URL de conexão com o banco de dados recém-criado
DATABASE_URL = "postgresql://postgres:123@localhost/gamedex?client_encoding=utf8"

# Configura o SQLAlchemy para o banco de dados recém-criado
engine = create_engine(DATABASE_URL)
Base.metadata.bind = engine

# Testa a conexão com o banco de dados
try:
    with engine.connect() as connection:
        print("Conexão com o banco de dados bem-sucedida!")
except Exception as e:
    print(f"Erro ao conectar ao banco de dados: {e}")
    exit(1)  # Encerra o script se a conexão falhar

# Cria o banco de dados e as tabelas
try:
    print("Verificando banco de dados...")
    create_database()
    print("Criando tabelas no banco de dados...")
    Base.metadata.create_all(bind=engine)
    print("Tabelas criadas com sucesso!")
except Exception as e:
    print(f"Erro ao criar tabelas: {e}")