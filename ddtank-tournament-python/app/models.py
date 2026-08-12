from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class Tournament(Base):
    __tablename__ = "tournaments"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    status = Column(String, default="open", nullable=False)
    max_players = Column(Integer, default=32)
    prize = Column(String)
    scheduled_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    players = relationship("Player", back_populates="tournament", cascade="all, delete-orphan")
    matches = relationship("Match", back_populates="tournament", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_tournaments_status", "status"),
        Index("ix_tournaments_scheduled_at", "scheduled_at"),
    )

class Player(Base):
    __tablename__ = "players"

    id = Column(Integer, primary_key=True, index=True)
    nickname = Column(String, nullable=False)
    server = Column(String, nullable=False)
    level = Column(Integer)
    power = Column(Integer)
    guild = Column(String)
    tournament_id = Column(Integer, ForeignKey("tournaments.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    tournament = relationship("Tournament", back_populates="players")
    matches_as_a = relationship("Match", foreign_keys="Match.player_a_id", back_populates="player_a")
    matches_as_b = relationship("Match", foreign_keys="Match.player_b_id", back_populates="player_b")
    wins = relationship("Match", foreign_keys="Match.winner_id", back_populates="winner")

    __table_args__ = (
        Index("ix_players_tournament_id", "tournament_id"),
        Index("ix_players_nickname_tournament", "nickname", "tournament_id", unique=True),
    )

class Match(Base):
    __tablename__ = "matches"

    id = Column(Integer, primary_key=True, index=True)
    round = Column(Integer, nullable=False)
    position = Column(Integer, nullable=False)
    status = Column(String, default="pending", nullable=False)
    score_a = Column(Integer, default=0)
    score_b = Column(Integer, default=0)
    tournament_id = Column(Integer, ForeignKey("tournaments.id", ondelete="CASCADE"), nullable=False)
    player_a_id = Column(Integer, ForeignKey("players.id", ondelete="SET NULL"))
    player_b_id = Column(Integer, ForeignKey("players.id", ondelete="SET NULL"))
    winner_id = Column(Integer, ForeignKey("players.id", ondelete="SET NULL"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    tournament = relationship("Tournament", back_populates="matches")
    player_a = relationship("Player", foreign_keys=[player_a_id], back_populates="matches_as_a")
    player_b = relationship("Player", foreign_keys=[player_b_id], back_populates="matches_as_b")
    winner = relationship("Player", foreign_keys=[winner_id], back_populates="wins")

    __table_args__ = (
        Index("ix_matches_tournament_id", "tournament_id"),
        Index("ix_matches_tournament_round", "tournament_id", "round"),
        Index("ix_matches_player_a_id", "player_a_id"),
        Index("ix_matches_player_b_id", "player_b_id"),
        Index("ix_matches_winner_id", "winner_id"),
    )
