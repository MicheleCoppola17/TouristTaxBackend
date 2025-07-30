from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict
import pandas as pd
import tempfile
import os

app = FastAPI()

#CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins = ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)) -> List[Dict]:
    suffix = ".xls"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name

        try:
            df = pd.read_excel(tmp_path)

            bookings = []
            for _, row in df.iterrows():
                bookings.append({
                    "date": pd.to_datetime(row["Arrivo"]).strftime("%Y-%m-%d") if not pd.isna(row["Arrivo"]) else None,
                    "numberOfGuests": int(row["Adulti"]) if not pd.isna(row["Adulti"]) else 0,
                    "numberOfNights": int(row["Durata (notti)"]) if not pd.isna(row["Durata (notti)"]) else 0
                })

            return bookings
        finally:
            os.unlink(tmp_path)
