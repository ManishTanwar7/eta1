# Ops Dashboard (FastAPI + Jinja2)

A minimal FastAPI project that loads JSON datasets from `datasets/` and
renders them as tables on a `/dashboard` page. Includes a `/health` endpoint
and is ready to deploy on [Render](https://render.com).

## Project structure

```
.
├── main.py
├── requirements.txt
├── .env.example
├── .gitignore
├── templates/
│   └── dashboard.html
└── datasets/
    ├── gps_tracker.json
    ├── weather.json
    ├── delay_patterns.json
    ├── congestion.json
    ├── signal_aspects.json
    └── station_ops.json
```

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate   # on Windows: .venv\Scripts\activate

cp .env.example .env

pip install -r requirements.txt
uvicorn main:app --reload
```

Then open:
- http://127.0.0.1:8000/health
- http://127.0.0.1:8000/dashboard

## Deploy on Render

1. Push this project to a GitHub/GitLab repo.
2. In Render, create a new **Web Service** from that repo.
3. Set:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn main:app --host 0.0.0.0 --port 10000`
4. Add environment variable `USE_MOCK_DATA=true` (from `.env.example`) in the
   Render dashboard's Environment tab.
5. Deploy. Once live, check `https://<your-service>.onrender.com/health`.

## Notes

- Adding/removing a `.json` file in `datasets/` won't automatically appear
  on the dashboard — register it (key + title) in `DATASET_LABELS` in
  `main.py`.
- Each dataset file may be a plain JSON array of row objects, or an object
  with a `data` or `rows` key containing that array.
