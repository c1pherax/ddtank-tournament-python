<div align="center">

# 🏆 DDTank Tournament Manager

*Sistema para organizar torneios de DDTank.*

[![Python](https://img.shields.io/badge/Python-3.12-blue?style=flat-square&logo=python)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green?style=flat-square&logo=fastapi)](https://fastapi.tiangolo.com)
[![License](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)](LICENSE)

</div>

---

## O que é isso?

É um auxiliar pra você criar torneios de DDTank. Você cadastra os jogadores, aperte um botão e o sistema monta a chave de mata-mata sozinho. Depois é só ir clicando no vencedor de cada partida até descobrir o campeão.

---

## O que dá pra fazer?

- Criar torneio com nome, descrição, prêmio, data e limite de jogadores
- Editar as informações depois
- Cadastrar jogadores (nickname, servidor, level, fc, guilda)
- Gerar a chave de mata-mata automaticamente (com embaralhamento e bye)
- Definir o vencedor de cada partida com um clique
- A próxima rodada cria sozinha quando todos terminam
- Cancelar ou finalizar o torneio quando quiser

---

## Tecnologias

- **Python 3.12** + **FastAPI** — o backend
- **SQLite** — banco de dados (não precisa instalar nada)
- **Jinja2** — páginas HTML
- **CSS puro** — tema escuro com glassmorphism e animações

---

## Como rodar

### 1. Baixe o projeto
```bash
git clone https://github.com/c1pherax/ddtank-tournament-python.git
cd ddtank-tournament-python
```

### 2. Instale as dependências
```bash
pip install -r requirements.txt
```

### 3. Rode
```bash
python -m uvicorn app.main:app --reload
```

### 4. Abra no navegador
**http://localhost:8000**

---

## Com Docker (se preferir)

```bash
docker compose up
```

Acesse **http://localhost:8000**

---

## Testes

```bash
pytest tests/ -v
```

---

## Estrutura

```
ddtank-tournament-python/
├── app/              # Código Python (FastAPI, models, rotas, lógica)
├── templates/        # Páginas HTML
├── static/css/       # Estilos visuais
├── tests/            # Testes
├── requirements.txt  # Dependências
├── Dockerfile        # Docker
├── docker-compose.yml
└── README.md         # Você está aqui
```

---

## Como funciona na prática

1. Crie o torneio
2. Cadastre os jogadores
3. Clice em "Iniciar Torneio" → gere a chave
4. Vai no mata-mata e clice no vencedor de cada partida
5. O sistema avança sozinho pra próxima rodada
6. Repete até a final
7. Campeão definido! 🏆

---

## Próximas ideias

- [ ] Double elimination (repescagem)
- [ ] Ranking de jogadores
- [ ] Notificar no Discord
- [ ] Exportar a chave como imagem PNG
- [ ] Login pra administradores
- [ ] Foto de perfil dos jogadores

---

## Quer contribuir?

1. De um fork
2. Crie uma branch: `git checkout -b sua-feature`
3. Commita: `git commit -m "Adicionei X"`
4. Push: `git push origin sua-feature`
5. Abre um Pull Request

---

## Licença

MIT — use à vontade.

---

<div align="center">

Feito com 💜 por **c1pherax**

</div>
