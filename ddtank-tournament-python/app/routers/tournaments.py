from fastapi import APIRouter, Depends, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.database import get_db
from app.services import tournament_service as service
from app import schemas

router = APIRouter(prefix="/tournaments", tags=["tournaments"])

# ============================================================
# ROTAS HTML (estaticas primeiro)
# ============================================================

@router.get("/view", response_class=HTMLResponse)
def page_list_tournaments(request: Request, status: Optional[str] = None, db: Session = Depends(get_db)):
    from fastapi.templating import Jinja2Templates
    templates = Jinja2Templates(directory="templates")

    if status == "open":
        tournaments = service.list_active_tournaments(db)
    else:
        tournaments = service.list_tournaments(db)

    return templates.TemplateResponse("tournaments/list.html", {
        "request": request,
        "tournaments": tournaments,
        "filter_status": status
    })

@router.get("/view/new", response_class=HTMLResponse)
def page_new_tournament(request: Request):
    from fastapi.templating import Jinja2Templates
    templates = Jinja2Templates(directory="templates")
    return templates.TemplateResponse("tournaments/form.html", {"request": request, "tournament": None, "mode": "create"})

@router.post("/view/new")
def page_create_tournament(
    request: Request,
    name: str = Form(...),
    description: Optional[str] = Form(None),
    max_players: int = Form(32),
    prize: Optional[str] = Form(None),
    scheduled_at: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    scheduled_dt = None
    if scheduled_at:
        try:
            scheduled_dt = datetime.fromisoformat(scheduled_at)
        except:
            pass

    tournament_data = schemas.TournamentCreate(
        name=name,
        description=description,
        max_players=max_players,
        prize=prize,
        scheduled_at=scheduled_dt
    )
    service.create_tournament(db, tournament_data)
    return RedirectResponse(url="/tournaments/view", status_code=303)

@router.get("/view/{tournament_id}", response_class=HTMLResponse)
def page_tournament_detail(request: Request, tournament_id: int, db: Session = Depends(get_db)):
    from fastapi.templating import Jinja2Templates
    templates = Jinja2Templates(directory="templates")

    tournament = service.get_tournament(db, tournament_id)
    if not tournament:
        raise HTTPException(status_code=404, detail="Torneio nao encontrado")

    return templates.TemplateResponse("tournaments/detail.html", {
        "request": request,
        "tournament": tournament
    })

@router.get("/view/{tournament_id}/edit", response_class=HTMLResponse)
def page_edit_tournament(request: Request, tournament_id: int, db: Session = Depends(get_db)):
    from fastapi.templating import Jinja2Templates
    templates = Jinja2Templates(directory="templates")

    tournament = service.get_tournament(db, tournament_id)
    if not tournament:
        raise HTTPException(status_code=404, detail="Torneio nao encontrado")

    return templates.TemplateResponse("tournaments/form.html", {
        "request": request,
        "tournament": tournament,
        "mode": "edit"
    })

@router.post("/view/{tournament_id}/edit")
def page_update_tournament(
    request: Request,
    tournament_id: int,
    name: str = Form(...),
    description: Optional[str] = Form(None),
    max_players: int = Form(32),
    prize: Optional[str] = Form(None),
    scheduled_at: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    tournament = service.get_tournament(db, tournament_id)
    if not tournament:
        raise HTTPException(status_code=404, detail="Torneio nao encontrado")

    scheduled_dt = None
    if scheduled_at:
        try:
            scheduled_dt = datetime.fromisoformat(scheduled_at)
        except:
            pass

    updates = schemas.TournamentUpdate(
        name=name,
        description=description,
        max_players=max_players,
        prize=prize,
        scheduled_at=scheduled_dt
    )
    service.update_tournament(db, tournament, updates)
    return RedirectResponse(url=f"/tournaments/view/{tournament_id}", status_code=303)

@router.post("/view/{tournament_id}/cancel")
def page_cancel_tournament(request: Request, tournament_id: int, db: Session = Depends(get_db)):
    tournament = service.get_tournament(db, tournament_id)
    if not tournament:
        raise HTTPException(status_code=404, detail="Torneio nao encontrado")

    updates = schemas.TournamentUpdate(status="cancelled")
    service.update_tournament(db, tournament, updates)
    return RedirectResponse(url="/tournaments/view", status_code=303)

@router.post("/view/{tournament_id}/finish")
def page_finish_tournament(request: Request, tournament_id: int, db: Session = Depends(get_db)):
    tournament = service.get_tournament(db, tournament_id)
    if not tournament:
        raise HTTPException(status_code=404, detail="Torneio nao encontrado")

    updates = schemas.TournamentUpdate(status="finished")
    service.update_tournament(db, tournament, updates)
    return RedirectResponse(url=f"/tournaments/view/{tournament_id}", status_code=303)

@router.post("/view/{tournament_id}/start")
def page_start_tournament(request: Request, tournament_id: int, db: Session = Depends(get_db)):
    tournament = service.get_tournament(db, tournament_id)
    if not tournament:
        raise HTTPException(status_code=404, detail="Torneio nao encontrado")
    if tournament.status != "open":
        return RedirectResponse(url=f"/tournaments/view/{tournament_id}", status_code=303)
    try:
        service.generate_bracket(db, tournament_id)
    except ValueError:
        pass
    return RedirectResponse(url=f"/matches/tournament/{tournament_id}/bracket", status_code=303)


# ============================================================
# ROTAS API
# ============================================================

@router.get("/", response_model=List[schemas.TournamentResponse])
def api_list_tournaments(status: Optional[str] = None, db: Session = Depends(get_db)):
    if status == "open":
        return service.list_active_tournaments(db)
    return service.list_tournaments(db)

@router.post("/", response_model=schemas.TournamentResponse, status_code=201)
def api_create_tournament(tournament: schemas.TournamentCreate, db: Session = Depends(get_db)):
    return service.create_tournament(db, tournament)

@router.get("/{tournament_id}", response_model=schemas.TournamentDetail)
def api_get_tournament(tournament_id: int, db: Session = Depends(get_db)):
    tournament = service.get_tournament(db, tournament_id)
    if not tournament:
        raise HTTPException(status_code=404, detail="Torneio nao encontrado")
    return tournament

@router.put("/{tournament_id}", response_model=schemas.TournamentResponse)
def api_update_tournament(tournament_id: int, updates: schemas.TournamentUpdate, db: Session = Depends(get_db)):
    tournament = service.get_tournament(db, tournament_id)
    if not tournament:
        raise HTTPException(status_code=404, detail="Torneio nao encontrado")
    return service.update_tournament(db, tournament, updates)

@router.delete("/{tournament_id}", status_code=204)
def api_delete_tournament(tournament_id: int, db: Session = Depends(get_db)):
    tournament = service.get_tournament(db, tournament_id)
    if not tournament:
        raise HTTPException(status_code=404, detail="Torneio nao encontrado")
    service.delete_tournament(db, tournament)
    return {"ok": True}

@router.post("/{tournament_id}/start", response_model=schemas.TournamentResponse)
def api_start_tournament(tournament_id: int, db: Session = Depends(get_db)):
    tournament = service.get_tournament(db, tournament_id)
    if not tournament:
        raise HTTPException(status_code=404, detail="Torneio nao encontrado")
    if tournament.status != "open":
        raise HTTPException(status_code=400, detail="Torneio ja foi iniciado ou finalizado")
    try:
        return service.generate_bracket(db, tournament_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
