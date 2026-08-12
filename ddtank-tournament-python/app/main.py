from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

from app.database import engine, Base
from app.routers import tournaments, players, matches

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="DDTank Tournament Manager",
    description="Sistema de gerenciamento de torneios DDTank com bracket automático, inscrição de jogadores e acompanhamento em tempo real. Feito com Python + FastAPI.",
    version="1.0.0",
)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

app.include_router(tournaments.router)
app.include_router(players.router)
app.include_router(matches.router)

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("tournaments/list.html", {"request": request, "tournaments": [], "filter_status": None})

@app.get("/api/health")
def health_check():
    return {"status": "ok", "version": "1.0.0", "stack": "python"}
