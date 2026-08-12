from fastapi import APIRouter, Depends, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.services import tournament_service as service
from app import schemas

router = APIRouter(prefix="/players", tags=["players"])

# --- API Endpoints ---

@router.get("/tournament/{tournament_id}", response_model=list[schemas.PlayerResponse])
def api_list_players(tournament_id: int, db: Session = Depends(get_db)):
    return service.list_players(db, tournament_id)

@router.post("/tournament/{tournament_id}", response_model=schemas.PlayerResponse, status_code=201)
def api_register_player(tournament_id: int, player: schemas.PlayerCreate, db: Session = Depends(get_db)):
    tournament = service.get_tournament(db, tournament_id)
    if not tournament:
        raise HTTPException(status_code=404, detail="Torneio nao encontrado")
    if tournament.status != "open":
        raise HTTPException(status_code=400, detail="Inscricoes fechadas para este torneio")
    if len(tournament.players) >= tournament.max_players:
        raise HTTPException(status_code=400, detail="Limite de jogadores atingido")

    existing = [p for p in tournament.players if p.nickname.lower() == player.nickname.lower()]
    if existing:
        raise HTTPException(status_code=400, detail="Nickname ja registrado neste torneio")

    return service.register_player(db, tournament_id, player)

@router.delete("/{player_id}", status_code=204)
def api_remove_player(player_id: int, db: Session = Depends(get_db)):
    player = service.get_player(db, player_id)
    if not player:
        raise HTTPException(status_code=404, detail="Jogador nao encontrado")
    tournament = service.get_tournament(db, player.tournament_id)
    if tournament.status != "open":
        raise HTTPException(status_code=400, detail="Nao e possivel remover jogadores apos o inicio")
    service.remove_player(db, player)
    return {"ok": True}

# --- HTML Form (redirect) ---

@router.post("/tournament/{tournament_id}/register")
def page_register_player(
    request: Request,
    tournament_id: int,
    nickname: str = Form(...),
    server: str = Form(...),
    level: Optional[int] = Form(None),
    power: Optional[int] = Form(None),
    guild: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    player_data = schemas.PlayerCreate(
        nickname=nickname,
        server=server,
        level=level,
        power=power,
        guild=guild
    )
    try:
        service.register_player(db, tournament_id, player_data)
    except Exception:
        pass
    return RedirectResponse(url=f"/tournaments/view/{tournament_id}", status_code=303)
