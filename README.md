# Express Diagnostics Report Generator

Upload or paste a scan report, extract vehicle/DTC/ADAS information, and generate a branded PDF report.

## Run locally

```bash
cd express_report_generator
python -m venv .venv
.venv\Scripts\activate  # Windows
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open: http://127.0.0.1:8000

## Deploy to Render

1. Push this folder to GitHub.
2. Create a new Render Web Service.
3. Build Command: `pip install -r requirements.txt`
4. Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. Render will install Tesseract using `apt.txt`.

## Environment variables

Optional:

- `APP_PASSWORD` - requires employees to enter this password before generating reports.
- `COMPANY_NAME` - defaults to Express Diagnostics.
- `COMPANY_TAGLINE` - defaults to Precision. Safety. Confidence.
