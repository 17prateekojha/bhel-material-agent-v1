# BHEL TBG HVDC Nagpur Material Management Agent — V1

## Features

- Daily material receipt entry
- Material register
- Material event history
- Handover, damage and shortage tracking
- Reconciliation
- Exception detection
- Excel export
- LangGraph AI agent
- SQLite database

## Recommended Python

Use Python 3.12 or 3.13 for the first installation. This avoids compatibility issues that can occur with some AI packages on very new Python releases.

## Windows setup

```powershell
cd bhel_material_agent_v1
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
copy .env.example .env
```

## Start Ollama

Install Ollama separately, then:

```powershell
ollama pull qwen2.5:3b
ollama serve
```

If the model is already installed, `ollama serve` is enough.

## Run application

```powershell
streamlit run app.py
```

Open the displayed localhost URL.

## Test

```powershell
pytest -q
```

## V1 database

SQLite is used by default:

`data/materials.db`

To move to PostgreSQL later, set `DATABASE_URL` in `.env`, for example:

```text
DATABASE_URL=postgresql+psycopg://user:password@localhost/materials
```

and add an appropriate PostgreSQL driver.

## Current AI tools

- Search by Material ID
- Search by description/item/PO/supplier
- Find reconciliation exceptions

The database remains the source of truth. The LLM does not directly write database records.

## Online deployment setup

### Option 1: Streamlit Community Cloud (fastest)

1. Push the project to GitHub.
2. Create a new app in Streamlit Community Cloud.
3. Set these secrets in the app:
   - `DATABASE_URL` = your hosted PostgreSQL URL
   - `OPENAI_API_KEY` = your OpenAI API key
   - `OPENAI_MODEL` = `gpt-4o-mini` (or another supported model)
4. Keep `OLLAMA_MODEL` and `OLLAMA_BASE_URL` unset unless you want to use local Ollama.
5. Deploy.

Example PostgreSQL URL:

```text
DATABASE_URL=postgresql+psycopg2://user:password@host:5432/dbname
```

### Option 2: Render or Railway

1. Create a web service from the repository.
2. Add the same environment variables.
3. Use a managed PostgreSQL add-on.
4. Start the app with:

```text
streamlit run app.py --server.address 0.0.0.0 --server.port $PORT
```

### Required dependency changes for cloud hosting

The app now supports either:

- OpenAI via `OPENAI_API_KEY` and `OPENAI_MODEL`, or
- Ollama via `OLLAMA_MODEL` and `OLLAMA_BASE_URL`

If you use the cloud-hosted OpenAI path, no local Ollama server is needed.
