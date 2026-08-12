"""
Serviço de torneios DDTank - toda a lógica de negócio.
"""
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import desc, asc
from typing import List, Optional
import random

from app.models import Tournament, Player, Match
from app.schemas import TournamentCreate, TournamentUpdate, PlayerCreate, MatchCreate, MatchUpdate

# --- Torneios ---

def list_tournaments(db: Session) -> List[Tournament]:
    return db.query(Tournament).order_by(desc(Tournament.created_at)).all()

def list_active_tournaments(db: Session) -> List[Tournament]:
    return db.query(Tournament).filter(Tournament.status == "open").order_by(desc(Tournament.created_at)).all()

def get_tournament(db: Session, tournament_id: int) -> Optional[Tournament]:
    return db.query(Tournament).options(
        joinedload(Tournament.players),
        joinedload(Tournament.matches).joinedload(Match.player_a),
        joinedload(Tournament.matches).joinedload(Match.player_b),
        joinedload(Tournament.matches).joinedload(Match.winner),
    ).filter(Tournament.id == tournament_id).first()

def create_tournament(db: Session, tournament: TournamentCreate) -> Tournament:
    db_tournament = Tournament(**tournament.model_dump())
    db.add(db_tournament)
    db.commit()
    db.refresh(db_tournament)
    return db_tournament

def update_tournament(db: Session, tournament: Tournament, updates: TournamentUpdate) -> Tournament:
    for field, value in updates.model_dump(exclude_unset=True).items():
        setattr(tournament, field, value)
    db.commit()
    db.refresh(tournament)
    return tournament

def delete_tournament(db: Session, tournament: Tournament) -> None:
    db.delete(tournament)
    db.commit()

# --- Jogadores ---

def list_players(db: Session, tournament_id: int) -> List[Player]:
    return db.query(Player).filter(Player.tournament_id == tournament_id).order_by(asc(Player.created_at)).all()

def get_player(db: Session, player_id: int) -> Optional[Player]:
    return db.query(Player).filter(Player.id == player_id).first()

def register_player(db: Session, tournament_id: int, player: PlayerCreate) -> Player:
    db_player = Player(tournament_id=tournament_id, **player.model_dump())
    db.add(db_player)
    db.commit()
    db.refresh(db_player)
    return db_player

def remove_player(db: Session, player: Player) -> None:
    db.delete(player)
    db.commit()

# --- Partidas ---

def list_matches(db: Session, tournament_id: int) -> List[Match]:
    return db.query(Match).options(
        joinedload(Match.player_a),
        joinedload(Match.player_b),
        joinedload(Match.winner),
    ).filter(Match.tournament_id == tournament_id).order_by(asc(Match.round), asc(Match.position)).all()

def get_match(db: Session, match_id: int) -> Optional[Match]:
    return db.query(Match).options(
        joinedload(Match.player_a),
        joinedload(Match.player_b),
        joinedload(Match.winner),
    ).filter(Match.id == match_id).first()

def create_match(db: Session, match: MatchCreate) -> Match:
    db_match = Match(**match.model_dump())
    db.add(db_match)
    db.commit()
    db.refresh(db_match)
    return db_match

def update_match(db: Session, match: Match, updates: MatchUpdate) -> Match:
    for field, value in updates.model_dump(exclude_unset=True).items():
        setattr(match, field, value)
    db.commit()
    db.refresh(match)
    return match

def set_winner(db: Session, match: Match, player_id: int) -> Match:
    match.winner_id = player_id
    match.status = "finished"
    db.commit()
    db.refresh(match)
    return match

# --- Geração de bracket (single elimination) ---

def generate_bracket(db: Session, tournament_id: int) -> Tournament:
    players = list_players(db, tournament_id)

    if len(players) < 2:
        raise ValueError("Precisa de pelo menos 2 jogadores para gerar o bracket")

    tournament = db.query(Tournament).filter(Tournament.id == tournament_id).first()
    if not tournament:
        raise ValueError("Torneio não encontrado")

    tournament.status = "ongoing"
    db.commit()

    shuffled = players[:]
    random.shuffle(shuffled)

    i = 0
    position = 1
    while i < len(shuffled):
        p1 = shuffled[i]
        if i + 1 < len(shuffled):
            p2 = shuffled[i + 1]
            db_match = Match(
                tournament_id=tournament_id,
                round=1,
                position=position,
                player_a_id=p1.id,
                player_b_id=p2.id,
                status="pending"
            )
        else:
            db_match = Match(
                tournament_id=tournament_id,
                round=1,
                position=position,
                player_a_id=p1.id,
                player_b_id=None,
                winner_id=p1.id,
                status="finished"
            )
        db.add(db_match)
        i += 2
        position += 1

    db.commit()
    db.refresh(tournament)
    return tournament

def advance_winners(db: Session, tournament_id: int, round: int) -> dict:
    matches = db.query(Match).filter(
        Match.tournament_id == tournament_id,
        Match.round == round,
        Match.status == "finished"
    ).order_by(asc(Match.position)).all()

    winners = [m.winner_id for m in matches if m.winner_id is not None]

    if len(winners) < 2:
        tournament = db.query(Tournament).filter(Tournament.id == tournament_id).first()
        tournament.status = "finished"
        db.commit()
        return {"status": "tournament_finished", "champion_id": winners[0] if winners else None}

    i = 0
    position = 1
    while i < len(winners):
        w1 = winners[i]
        if i + 1 < len(winners):
            w2 = winners[i + 1]
            db_match = Match(
                tournament_id=tournament_id,
                round=round + 1,
                position=position,
                player_a_id=w1,
                player_b_id=w2,
                status="pending"
            )
        else:
            db_match = Match(
                tournament_id=tournament_id,
                round=round + 1,
                position=position,
                player_a_id=w1,
                player_b_id=None,
                winner_id=w1,
                status="finished"
            )
        db.add(db_match)
        i += 2
        position += 1

    db.commit()
    return {"status": "next_round_created", "round": round + 1, "matches": (len(winners) + 1) // 2}
