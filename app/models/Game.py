from sqlalchemy import Column, Integer, String, ForeignKey, Text, Date
from sqlalchemy.orm import relationship
from app.database import Base

class UserGame(Base):
    __tablename__ = "user_games"
    user_id = Column(Integer, ForeignKey('users.id'), primary_key=True)
    game_id = Column(Integer, ForeignKey('games.id'), primary_key=True)
    comment = Column(Text)
    rating = Column(Integer)  # 0 a 100
    progress = Column(String)  # Exemplo: "Zerado", "Em andamento", "Platinado", etc.
    status = Column(String, default="jogado")  # Novo campo: "jogado"
    user = relationship("User", back_populates="user_games")
    game = relationship("Game", back_populates="user_games")

class Game(Base):
    __tablename__ = "games"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    rawg_id = Column(Integer, unique=True)
    background_img = Column(String)  # URL da imagem
    platforms = Column(String)       # Exemplo: "PC, PS5, Xbox"
    release_date = Column(Date, nullable=True)
    user_games = relationship("UserGame", back_populates="game")

# No modelo User.py, adicione:
# user_games = relationship("UserGame", back_populates="user")