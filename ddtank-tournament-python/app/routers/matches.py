from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.services import tournament_service as service
from app import schemas

router = APIRouter(prefix="/matches", tags=["matches"])

# --- API Endpoints ---

@router.get("/tournament/{tournament_id}", response_model=list[schemas.MatchResponse])
def api_list_matches(tournament_id: int, db: Session = Depends(get_db)):
    return service.list_matches(db, tournament_id)

@router.get("/{match_id}", response_model=schemas.MatchResponse)
def api_get_match(match_id: int, db: Session = Depends(get_db)):
    match = service.get_match(db, match_id)
    if not match:
        raise HTTPException(status_code=404, detail="Partida nao encontrada")
    return match

@router.post("/{match_id}/winner/{player_id}", response_model=schemas.MatchResponse)
def api_set_winner(match_id: int, player_id: int, db: Session = Depends(get_db)):
    match = service.get_match(db, match_id)
    if not match:
        raise HTTPException(status_code=404, detail="Partida nao encontrada")
    if match.status == "finished":
        raise HTTPException(status_code=400, detail="Partida ja finalizada")
    if player_id not in [match.player_a_id, match.player_b_id]:
        raise HTTPException(status_code=400, detail="Jogador nao participa desta partida")

    updated = service.set_winner(db, match, player_id)

    round_matches = service.list_matches(db, match.tournament_id)
    current_round = match.round
    round_finished = all(
        m.status == "finished" for m in round_matches if m.round == current_round
    )

    if round_finished:
        service.advance_winners(db, match.tournament_id, current_round)

    return updated

# --- HTML Bracket View ---

@router.get("/tournament/{tournament_id}/bracket", response_class=HTMLResponse)
def page_bracket(request: Request, tournament_id: int, db: Session = Depends(get_db)):
    from fastapi.templating import Jinja2Templates
    templates = Jinja2Templates(directory="templates")

    tournament = service.get_tournament(db, tournament_id)
    if not tournament:
        raise HTTPException(status_code=404, detail="Torneio nao encontrado")

    matches = service.list_matches(db, tournament_id)

    rounds = {}
    for m in matches:
        if m.round not in rounds:
            rounds[m.round] = []
        rounds[m.round].append(m)

    champion = None
    if tournament.status == "finished":
        for m in matches:
            if m.winner:
                champion = m.winner

    return templates.TemplateResponse("bracket.html", {
        "request": request,
        "tournament": tournament,
        "rounds": rounds,
        "champion": champion
    })

# --- HTML Actions (redirect back to bracket) ---

@router.post("/{match_id}/winner/{player_id}/redirect")
def page_set_winner_redirect(match_id: int, player_id: int, db: Session = Depends(get_db)):
    match = service.get_match(db, match_id)
    if not match:
        raise HTTPException(status_code=404, detail="Partida nao encontrada")
    if match.status == "finished":
        return RedirectResponse(url=f"/matches/tournament/{match.tournament_id}/bracket", status_code=303)
    if player_id not in [match.player_a_id, match.player_b_id]:
        raise HTTPException(status_code=400, detail="Jogador nao participa desta partida")

    updated = service.set_winner(db, match, player_id)

    round_matches = service.list_matches(db, match.tournament_id)
    current_round = match.round
    round_finished = all(
        m.status == "finished" for m in round_matches if m.round == current_round
    )

    if round_finished:
        service.advance_winners(db, match.tournament_id, current_round)

    return RedirectResponse(url=f"/matches/tournament/{match.tournament_id}/bracket", status_code=303)
