import os
import pandas as pd
from fastapi import FastAPI, UploadFile, HTTPException
from fastapi.responses import FileResponse

from classify import classify

app = FastAPI()

@app.post("/classify/")
async def classify_logs(file: UploadFile):
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="File must be a CSV.")
    
    try:
        # Read the uploaded CSV
        df = pd.read_csv(file.file)
        if "source" not in df.columns or "log_message" not in df.columns:
            raise HTTPException(status_code=400, detail="CSV must contain 'source' and 'log_message' columns.")
        
        # Perform classification
        df["target_label"] = classify(list(zip(df["source"], df["log_message"])))

        # Ensure resources directory exists
        output_dir = "resources"
        os.makedirs(output_dir, exist_ok=True)
        output_file = os.path.join(output_dir, "output.csv")

        # Save the modified file
        df.to_csv(output_file, index=False)
        return FileResponse(output_file, media_type='text/csv')
    except PermissionError:
        raise HTTPException(status_code=500, detail="Permission denied. Check directory permissions.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        file.file.close()
