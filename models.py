from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), nullable=False)
    correo = Column(String(100), unique=True, index=True, nullable=False)
    password = Column(String(255), nullable=False)
    tokenU = Column(String(255), unique=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relaciones
    salas = relationship("Sala", back_populates="user")
    user_salas = relationship("UserSala", back_populates="user")

class Sala(Base):
    __tablename__ = "salas"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), nullable=False)
    description = Column(Text)
    xml = Column(Text)
    tokenS = Column(String(255), unique=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relaciones
    user = relationship("User", back_populates="salas")
    user_salas = relationship("UserSala", back_populates="sala")

class UserSala(Base):
    __tablename__ = "userSalas"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    salas_id = Column(Integer, ForeignKey("salas.id"), nullable=False)
    
    # Relaciones
    user = relationship("User", back_populates="user_salas")
    sala = relationship("Sala", back_populates="user_salas")