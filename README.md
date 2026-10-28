---
title: Poetry Chef
emoji: 📚
colorFrom: blue
colorTo: indigo
sdk: docker
pinned: false
---

# Poetry Chef — Hầm cho rục, kho cho thắm

## Overview

Poetry Chef "cooks" a user's emotion using real recipes from early 20th-century Vietnamese women's newspapers, *Nữ Giới Chung* (1918) and *Phụ Nữ Tân Văn* (1929). The user types an emotion (e.g. *cô đơn*) and how heavy it feels. The app picks a historical recipe and rewrites it almost word-for-word, with the emotion as its main ingredient, then cites the original article.

The project is part of Digitizing Việt Nam. It's meant to bring archival Quốc ngữ cooking texts to new readers through a playful, poetic interaction. Domain terms used below are defined in [GLOSSARY.md](GLOSSARY.md).

## Feature Highlights

- **Archival recipes, kept verbatim**: the "Cách làm" section copies the original newspaper text (Nguyên văn), keeping its 1918/1929 spelling and style.
- **Emotion as ingredient**: the main ingredient is replaced by the user's Emotion. Classifiers like *con*, *cái* are adjusted so the sentence still reads naturally.
- **Weight**: a slider lets the user say how heavy the Emotion is (e.g. *5 kg*). This becomes the quantity in the recipe.
- **Spontaneity**: each request draws a random Original Recipe and a random Poetic Imagery, so the same Emotion yields a new dish every time.
- **Citations**: every result shows the source newspaper, issue and date, with dates rendered in Vietnamese.
- **Printable**: the frontend styles the result as a printable recipe card.

## Tech Stack

- **Backend**: Python 3.11, FastAPI, Uvicorn, Pydantic Settings
- **LLM**: OpenAI GPT (`gpt-4o-mini` by default) via LangChain (`langchain-openai`)
- **Data**: a curated CSV of historical recipes (`data/data.csv`)
- **Frontend**: React 18, TypeScript, Vite
- **Deployment**: Docker (Hugging Face Spaces, port 7860)

## Technical Description

### Architecture

```text
Browser (React/Vite)
   │  POST /ask { question: Emotion, additional_context: Weight }
   ▼
FastAPI (app/main.py)
   │
   ▼
PoetryChefService (app/service.py)
   ├─ load data/data.csv (cached in memory)
   ├─ pick a random Original Recipe + random Poetic Imagery
   └─ prompt OpenAI GPT ──► Re-cooked Recipe
   │
   ▼
{ answer, citations, sources } ──► rendered as a recipe card
```

### Components

| Path                  | Role                                                                     |
| --------------------- | ------------------------------------------------------------------------ |
| `app/main.py`         | FastAPI app, CORS, and the `/`, `/health`, `/ask` endpoints              |
| `app/service.py`      | Loads recipes, random selection, the prompt, and the OpenAI call         |
| `app/schemas.py`      | Request/response models                                                  |
| `app/settings.py`     | Reads configuration from environment variables / `.env`                 |
| `app/deps.py`         | FastAPI dependency wiring (one shared service per process)               |
| `data/data.csv`       | Original Recipes: action, dish name, date, issue, newspaper, Nguyên văn  |
| `frontend/src/App.tsx`| Emotion + Weight form and the result card                                |
| `frontend/src/client.ts` | Fetch client for `POST /ask`                                          |

### How it works

1. The frontend sends the Emotion as `question` and the Weight as `additional_context` (e.g. `"5 kg"`).
2. The service loads the recipe CSV once and keeps it in memory.
3. One recipe is picked at **random** rather than by similarity search. A vector database would add cost and latency without improving results here: the dataset is small, and matching an emotion against cooking text isn't meaningful. The randomness is part of the experience.
4. The system prompt tells GPT to:
   - copy the Nguyên văn word-for-word
   - swap only the main ingredient for the Emotion
   - use the random Poetic Imagery only in "Cách thưởng thức"
   - avoid explanations and similes
5. The response carries the generated text plus the source recipe, so the frontend can show the citation.

The full API contract is in [API.md](API.md).

## Installation

### Prerequisites

- Python 3.10+
- Node.js 18+ and npm
- An **OpenAI API key**, used for chat completions. Create one at <https://platform.openai.com/api-keys>.

### 1. Backend

```bash
git clone <repo-url> Project_VSC3
cd Project_VSC3

python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env             # then edit .env and set OPENAI_API_KEY
uvicorn app.main:app --reload --port 8000
```

### 2. Frontend

```bash
cd frontend
cp .env.example .env             # points the UI at http://localhost:8000
npm install
npm run dev
```

Open <http://localhost:5173>.

### Environment variables

Backend (`.env`, see [.env.example](.env.example)):

| Variable          | Required | Default        | Description                                         |
| ----------------- | -------- | -------------- | --------------------------------------------------- |
| `OPENAI_API_KEY`  | Yes      | –              | OpenAI API key for chat completions                 |
| `CHAT_MODEL`      | No       | `gpt-4o-mini`  | OpenAI chat model                                   |
| `DATA_DIR`        | No       | `data`         | Folder containing `data.csv`                        |
| `ALLOWED_ORIGINS` | No       | `["*"]`        | JSON list of origins allowed by CORS                |

Frontend (`frontend/.env`, see [frontend/.env.example](frontend/.env.example)):

| Variable        | Required | Default                 | Description              |
| --------------- | -------- | ----------------------- | ------------------------ |
| `VITE_API_BASE` | No       | `http://localhost:8000` | Base URL of the backend  |

### Docker

```bash
docker build -t poetry-chef .
docker run -p 7860:7860 -e OPENAI_API_KEY=sk-... poetry-chef
```

## Example Usage

In the UI, type an Emotion, set the Weight slider, and submit. Or call the API directly:

```bash
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "nỗi nhớ", "additional_context": "3 kg"}'
```

Illustrative output (abridged; the actual text varies on every run), based on *Chả cá*, Phụ Nữ Tân Văn, 13/6/1929:

```text
Tên món: Chả nỗi nhớ
Nguyên liệu: Nỗi nhớ (3 kg), nước mắm, tiêu, lá chuối, mở
Cách làm: Nỗi nhớ rữa sạch rồi lóc ra làm hai. Lấy mũi giao nhỏ mà nạo lấy hết
  thịt nạc, còn xương với gia bỏ đi. Bỏ vô cối mà đâm cho nhuyễn rồi, nêm vô chút
  nước mắm và cho vô chút tiêu cho thơm. ...
Cách thưởng thức: Dọn ra khi hơi đất ẩm còn vương trên mái hiên, ăn chậm từng miếng.
Dựa trên: “Chả cá”. Phụ Nữ Tân Văn, số 7, ngày 13 tháng 6, 1929.
```

More inputs to try: *cô đơn* (10 kg), *trống rỗng* (1 kg), *thèm* (7 kg).
