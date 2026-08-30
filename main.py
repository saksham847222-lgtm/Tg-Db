from fastapi import FastAPI, Query, HTTPException
import duckdb

app = FastAPI(title="Telegram DB Search API")

# Hugging Face Parquet URL Pattern
HF_PARQUET_URL = "https://huggingface.co/datasets/Saksham4540/Telegram-DB/resolve/main/TG_DATA_PARTS/*/*.parquet"

@app.get("/")
def home():
    return {"status": "API Active", "endpoint": "/search?id=YOUR_10_DIGIT_ID"}

@app.get("/search")
def search_by_id(id: str = Query(..., description="10-digit Telegram User ID")):
    if not id.isdigit() or len(id) != 10:
        raise HTTPException(
            status_code=400, 
            detail="Invalid ID format. Please provide a valid 10-digit Telegram ID."
        )

    con = duckdb.connect()
    
    try:
        # Wildcard (*) allow karne ke liye ye setting execute karna zaroori hai
        con.execute("SET allow_asterisks_in_http_paths = true;")
        
        sql = f"""
            SELECT * 
            FROM read_parquet('{HF_PARQUET_URL}')
            WHERE CAST(id AS VARCHAR) = '{id}'
        """
        
        results = con.execute(sql).df().to_dict(orient="records")
        con.close()
        
        return {
            "status": "success",
            "query_id": id,
            "count": len(results),
            "data": results
        }
    except Exception as e:
        con.close()
        return {"status": "error", "message": str(e)}
