from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime

# --- Tournament ---
class TournamentBase(BaseModel):
    name: str = Field(..., min_length=1)
    description: Optional[str] = None
    status: str = Field(default="open", pattern="^(open|ongoing|finished|cancelled)$")
    max_players: int = Field(default=32, ge=2, le=128)
    prize: Optional[str] = None
    scheduled_at: Optional[datetime] = None

class TournamentCreate(TournamentBase):
    pass

class TournamentUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    max_players: Optional[int] = Field(default=None, ge=2, le=128)
    prize: Optional[str] = None
    scheduled_at: Optional[datetime] = None

class TournamentResponse(TournamentBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class TournamentDetail(TournamentResponse):
    players: List["PlayerResponse"] = []
    matches: List["MatchResponse"] = []

# --- Player ---
class PlayerBase(BaseModel):
    nickname: str = Field(..., min_length=2, max_length=30)
    server: str = Field(..., min_length=1)
    level: Optional[int] = Field(default=None, ge=1, le=100)
    power: Optional[int] = Field(default=None, ge=0)
    guild: Optional[str] = None

    @field_validator("level")
    @classmethod
    def validate_level(cls, v):
        if v is not None and (v < 1 or v > 100):
            raise ValueError("Level deve estar entre 1 e 100")
        return v

class PlayerCreate(PlayerBase):
    pass

class PlayerResponse(PlayerBase):
    id: int
    tournament_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# --- Match ---
class MatchBase(BaseModel):
    round: int = Field(..., gt=0)
    position: int = Field(..., gt=0)
    status: str = Field(default="pending", pattern="^(pending|ongoing|finished)$")
    score_a: int = Field(default=0, ge=0)
    score_b: int = Field(default=0, ge=0)

class MatchCreate(MatchBase):
    tournament_id: int
    player_a_id: Optional[int] = None
    player_b_id: Optional[int] = None
    winner_id: Optional[int] = None

class MatchUpdate(BaseModel):
    status: Optional[str] = None
    score_a: Optional[int] = None
    score_b: Optional[int] = None
    winner_id: Optional[int] = None

class MatchResponse(MatchBase):
    id: int
    tournament_id: int
    player_a_id: Optional[int] = None
    player_b_id: Optional[int] = None
    winner_id: Optional[int] = None
    player_a: Optional[PlayerResponse] = None
    player_b: Optional[PlayerResponse] = None
    winner: Optional[PlayerResponse] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Resolve forward references
TournamentDetail.model_rebuild()
