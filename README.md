<div align="center">

# 🏆 DDTank Tournament Manager

*Sistema pra organizar torneios de DDTank.*

[![Python](https://img.shields.io/badge/Python-3.12-blue?style=flat-square&logo=python)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green?style=flat-square&logo=fastapi)](https://fastapi.tiangolo.com)
[![License](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)](LICENSE)

</div>

---

## O que é isso?

É um site pra você criar torneios de DDTank. Você cadastra os jogadores, aperta um botão e o sistema monta a chave de mata-mata sozinho. Depois é só ir clicando no vencedor de cada partida até descobrir o campeão.

Tudo bonitinho, com tema escuro e efeitos de vidro (aquele estilo iOS).

---

## O que dá pra fazer?

- Criar torneio com nome, descrição, prêmio, data e limite de jogadores
- Editar as informações depois
- Cadastrar jogadores (nickname, servidor, level, power, guilda)
- Gerar a chave de mata-mata automaticamente (com embaralhamento e bye)
- Definir o vencedor de cada partida com um clique
- A próxima rodada cria sozinha quando todos terminam
- Cancelar ou finalizar o torneio quando quiser

---

## Como instalar e rodar (passo a passo)

> **Não sabe Python? Sem problema.** Siga os passos abaixo que vai dar certo.

### 1. Instalar o Python

O Python é a linguagem que faz o programa funcionar. Você precisa instalá-lo uma vez só.

1. Acesse: **https://www.python.org/downloads/**
2. Clique no botão grande amarelo que diz **"Download Python 3.12.x"**
3. Execute o arquivo baixado
4. Na primeira tela, **MARQUE** a caixinha que diz **"Add Python to PATH"** (é muito importante!)
5. Clique em **"Install Now"** e espere terminar
6. Feche a janela quando aparecer "Setup was successful"

**Verifique se instalou certo:**

Abra o Prompt de Comando (tecla Windows + R, digite `cmd` e aperte Enter) e digite:

```
python --version
```

Se aparecer algo como `Python 3.12.7`, deu certo! ✅

Se der erro, desinstale e reinstale marcando a caixinha do PATH.

---

### 2. Baixar este projeto

Clique no botão verde **"<> Code"** no topo desta página e depois em **"Download ZIP"**.

Ou, se tiver o Git instalado, rode no terminal:

```bash
git clone https://github.com/c1pherax/ddtank-tournament-python.git
```

---

### 3. Extrair o ZIP

1. Encontre o arquivo `ddtank-tournament-python.zip` na pasta Downloads
2. Clique com o botão direito → **"Extrair tudo..."**
3. Escolha uma pasta fácil de achar, tipo `C:\Projetos\ddtank-tournament-python`
4. Clique em **"Extrair"**

---

### 4. Instalar as dependências

As dependências são bibliotecas que o programa precisa pra funcionar. É tipo instalar os apps que seu celular precisa.

1. Abra o **Prompt de Comando** (tecla Windows + R, digite `cmd`, Enter)
2. Vá até a pasta do projeto. Digite:

```cmd
cd C:\Projetos\ddtank-tournament-python
```

> Troque `C:\Projetos\ddtank-tournament-python` pelo caminho onde você extraiu.

3. Agora instale tudo com um comando só:

```cmd
pip install -r requirements.txt
```

Espere terminar. Vai aparecer várias linhas de download — isso é normal.

---

### 5. Rodar o programa

Ainda no Prompt de Comando, na pasta do projeto, digite:

```cmd
python -m uvicorn app.main:app --reload
```

Se tudo der certo, você verá algo assim:

```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```

**Não feche essa janela!** Ela precisa ficar aberta enquanto você usa o programa.

---

### 6. Abrir no navegador

Abra seu navegador (Chrome, Edge, Firefox) e digite na barra de endereço:

```
http://localhost:8000
```

Ou clique aqui: **http://localhost:8000**

Pronto! O site vai aparecer. 🎉

---

### 7. Como parar o programa

Quando quiser parar, volte na janela do Prompt de Comando e aperte:

```
Ctrl + C
```

Depois confirme com `Y` e Enter.

---

## Com Docker (se preferir)

Se você já tem o Docker instalado, é mais fácil ainda:

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

1. Cria o torneio
2. Cadastra os jogadores
3. Clica em "Iniciar Torneio" → gera a chave
4. Vai no bracket e clica no vencedor de cada partida
5. O sistema avança sozinho pra próxima rodada
6. Repete até a final
7. Campeão definido! 🏆

---

## Deu erro? Veja aqui

| Erro | Solução |
|------|---------|
| `python não é reconhecido` | Reinstale o Python marcando "Add to PATH" |
| `pip não é reconhecido` | Reinstale o Python marcando "Add to PATH" |
| `No module named uvicorn` | Rode `pip install uvicorn` separadamente |
| `Address already in use` | Outro programa está usando a porta 8000. Feche-o ou use outra porta |
| Página não abre | Verifique se o Prompt de Comando ainda está rodando o servidor |

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
