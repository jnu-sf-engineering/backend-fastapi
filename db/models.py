from sqlalchemy import Column, String, DateTime, ForeignKey, BigInteger, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.mysql import TINYINT
from sqlalchemy.ext.declarative import declarative_base
from db.database import engine

Base = declarative_base()

# USER 테이블 구성
class User(Base):
    __tablename__ = "USER"

    USER_ID = Column(BigInteger, primary_key=True, autoincrement=True)
    EMAIL = Column(String(255), nullable=False, unique=True)
    PASSWORD = Column(String(255), nullable=False)
    NICKNAME = Column(String(255), nullable=False)

    projects = relationship("Project", back_populates="user")

# PROJECT 테이블 구성
class Project(Base):
    __tablename__ = "PROJECT"

    PROJECT_ID = Column(BigInteger, primary_key=True, autoincrement=True)
    USER_ID = Column(BigInteger, ForeignKey("USER.USER_ID"), nullable=False)
    PROJECT_NAME = Column(String(255), nullable=False)
    # SPRINT_COUNT DB 데이터 타입은 tinyint : 0 ~ 128
    SPRINT_COUNT = Column(TINYINT(display_width=1), nullable=True)
    MANAGER = Column(String(255), nullable=False)

    user = relationship("User", back_populates="projects")
    sprints = relationship("Sprint", back_populates="project")

# SUMMARY 테이블 구성
class Summary(Base):
    __tablename__ = "SUMMARY"

    SUMMARY_ID = Column(BigInteger, primary_key=True, autoincrement=True)
    PROJECT_ID = Column(BigInteger, ForeignKey("PROJECT.PROJECT_ID"), nullable=False)
    SUMMARY_CONTENT = Column(String(255), nullable=False)
    LAST_UPDATED = Column(DateTime(6), nullable=False)

    project = relationship("Project", back_populates="summaries")

Project.summaries = relationship("Summary", back_populates="project")

# SPRINT 테이블 구성
class Sprint(Base):
    __tablename__ = "SPRINT"

    SPRINT_ID = Column(BigInteger, primary_key=True, autoincrement=True)
    PROJECT_ID = Column(BigInteger, ForeignKey("PROJECT.PROJECT_ID"), nullable=False)
    SPRINT_NAME = Column(String(255), nullable=False)
    START_DATE = Column(DateTime(6), nullable=False)
    END_DATE = Column(DateTime(6), nullable=False)

    project = relationship("Project", back_populates="sprints")
    cards = relationship("Card", back_populates="sprint")
    retrospects = relationship("Retrospect", back_populates="sprint")

# CARD 테이블 구성
class Card(Base):
    __tablename__ = "CARD"

    CARD_ID = Column(BigInteger, primary_key=True, autoincrement=True)
    SPRINT_ID = Column(BigInteger, ForeignKey("SPRINT.SPRINT_ID"), nullable=False)
    CARD_CONTENT = Column(String(255), nullable=False)
    CARD_PARTICIPANTS = Column(String(255), nullable=False)
    CARD_STATUS = Column(Integer, nullable=False)

    sprint = relationship("Sprint", back_populates="cards")

# RETROSPECT 테이블 구성
class Retrospect(Base):
    __tablename__ = "RETROSPECT"

    RETRO_ID = Column(BigInteger, primary_key=True, autoincrement=True)
    SPRINT_ID = Column(BigInteger, ForeignKey("SPRINT.SPRINT_ID"), nullable=False)
    SUMMARY = Column(String(255), nullable=False)
    sprint = relationship("Sprint", back_populates="retrospects")
    kpt = relationship("KPT", uselist=False, back_populates="retrospect")
    four_ls = relationship("FourLs", uselist=False, back_populates="retrospect")
    css = relationship("CSS", uselist=False, back_populates="retrospect")

# KPT 테이블 구성
class KPT(Base):
    __tablename__ = "KPT"

    RETRO_ID = Column(BigInteger, ForeignKey("RETROSPECT.RETRO_ID"), primary_key=True)
    KEEP = Column(String(255), nullable=True)
    PROBLEM = Column(String(255), nullable=True)
    TRY = Column(String(255), nullable=True)

    retrospect = relationship("Retrospect", back_populates="kpt")

# FOUR_LS 테이블 구성
class FourLs(Base):
    __tablename__ = "FOUR_LS"

    RETRO_ID = Column(BigInteger, ForeignKey("RETROSPECT.RETRO_ID"), primary_key=True)
    LIKED = Column(String(255), nullable=True)
    LEARNED = Column(String(255), nullable=True)
    LACKED = Column(String(255), nullable=True)
    LOGGED_FOR = Column(String(255), nullable=True)

    retrospect = relationship("Retrospect", back_populates="four_ls")

# CSS 테이블 구성
class CSS(Base):
    __tablename__ = "CSS"

    RETRO_ID = Column(BigInteger, ForeignKey("RETROSPECT.RETRO_ID"), primary_key=True)
    CSS_CONTINUE = Column(String(255), nullable=True)
    CSS_STOP = Column(String(255), nullable=True)
    CSS_START = Column(String(255), nullable=True)

    retrospect = relationship("Retrospect", back_populates="css")

# 매퍼 추가
Base.metadata.create_all(bind=engine)
