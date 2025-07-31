from fastapi import FastAPI, File, UploadFile, HTTPException
from typing import List, Dict
import pandas as pd
import tempfile
import os

app = FastAPI()

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)) -> List[Dict]:
    # Check file type
    if not file.filename.endswith(('.xls', '.xlsx')):
        raise HTTPException(status_code=400, detail="File must be an Excel file (.xls or .xlsx)")
    
    # Determine suffix based on file extension
    suffix = ".xlsx" if file.filename.endswith('.xlsx') else ".xls"
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name
        
        try:
            df = pd.read_excel(tmp_path)
            bookings = []
            for _, row in df.iterrows():
                # If "Adulti" is empty, take number of guests from "Persone"
                number_of_guests = (
                    int(row["Adulti"]) if not pd.isna(row.get("Adulti"))
                    else int(row["Persone"]) if not pd.isna(row.get("Persone"))
                    else None
                )

                # Skip cancelled bookings
                if not pd.isna(row.get("Data di cancellazione")):
                    continue

                bookings.append({
                    "date": pd.to_datetime(row["Arrivo"]).strftime("%Y-%m-%d") if not pd.isna(row["Arrivo"]) else None,
                    "numberOfGuests": number_of_guests,
                    "numberOfNights": int(row["Durata (notti)"]) if not pd.isna(row["Durata (notti)"]) else 0
                })
            return bookings
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error processing Excel file: {str(e)}")
        finally:
            os.unlink(tmp_path)

@app.get("/health")
async def health_check():
    return {"status": "healthy"}