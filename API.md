# API Reference

Base URL (local): `http://localhost:8000` (Docker / Hugging Face Space: port `7860`).

Interactive docs are served by FastAPI at `/swagger` and `/redoc`.

All request and response bodies are JSON. Domain terms (Emotion, Weight, Original Recipe…) are defined in [GLOSSARY.md](GLOSSARY.md).

---

## `GET /health`

Liveness check.

**Response `200`**

```json
{ "status": "ok" }
```

**Example**

```bash
curl http://localhost:8000/health
```

---

## `GET /`

Same as `/health`. Used by hosting platforms that probe the root path.

**Response `200`**

```json
{ "status": "ok" }
```

---

## `POST /ask`

Re-cooks the user's Emotion: picks a random Original Recipe and a random Poetic Imagery, then asks the OpenAI chat model to rewrite the recipe with the Emotion as its main ingredient.

The same input can return a different recipe on each call; this is intentional.

### Request body

| Field                | Type   | Required | Description                                                         |
| -------------------- | ------ | -------- | ------------------------------------------------------------------- |
| `question`           | string | Yes      | The Emotion, at least 1 character (e.g. `"nỗi buồn"`).              |
| `additional_context` | string | No       | The Weight of the Emotion (e.g. `"5 kg"`). Defaults to "không xác định". |
| `temperature`        | number | No       | LLM temperature override, `0.0`–`2.0`. Defaults to `0.8`.           |

Unknown fields are ignored.

### Response `200`

| Field       | Type           | Description                                                  |
| ----------- | -------------- | ------------------------------------------------------------ |
| `answer`    | string         | The Re-cooked Recipe as Markdown-ish text (Tên món, Nguyên liệu, Cách làm, Cách thưởng thức, Dựa trên). |
| `citations` | string[]       | One label for the Original Recipe used: `"<dish> (<newspaper>, <date>)"`. |
| `sources`   | SourceChunk[]  | One entry describing the Original Recipe used.               |

`SourceChunk`:

| Field         | Type   | Description                                              |
| ------------- | ------ | -------------------------------------------------------- |
| `label`       | string | Dish, newspaper and date, with the date in Vietnamese.   |
| `book_title`  | string | Newspaper name (Báo).                                    |
| `chapter`     | string | Issue number (Số báo).                                   |
| `file_name`   | string | Data file the recipe came from (`data.csv`).             |
| `source_path` | string | Path of that data file on the server.                    |
| `text`        | string | Nguyên văn of the Original Recipe.                       |

If no recipe data is available, the endpoint still returns `200` with an apology in `answer` and empty `citations` / `sources`.

### Errors

| Status | When                                                        |
| ------ | ----------------------------------------------------------- |
| `422`  | `question` missing or empty, or `temperature` out of range. |
| `500`  | The OpenAI call failed (e.g. invalid `OPENAI_API_KEY`).     |

### Example

```bash
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "nỗi buồn", "additional_context": "5 kg"}'
```

```json
{
  "answer": "**Tên món**: Canh chua nỗi buồn\n**Nguyên liệu**: Nỗi buồn (5 kg), ...\n**Cách làm**: ...\n**Cách thưởng thức**: ... sương sớm ...\n**Dựa trên**: “Canh chua thơm”. Phụ Nữ Tân Văn, số 4, ngày 23 tháng 5, 1929.",
  "citations": ["Canh chua thơm (Phụ Nữ Tân Văn, May 23, 1929)"],
  "sources": [
    {
      "label": "Canh chua thơm (Phụ Nữ Tân Văn, 23 tháng 5, 1929)",
      "chapter": "4",
      "book_title": "Phụ Nữ Tân Văn",
      "file_name": "data.csv",
      "source_path": "/app/data/data.csv",
      "text": "..."
    }
  ]
}
```
