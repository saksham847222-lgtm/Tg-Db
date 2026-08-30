from fastapi import FastAPI, Query, HTTPException
import duckdb

app = FastAPI(title="Telegram DB Search API")

# Hugging Face internal URL pattern (hf:// protocol use karein)
HF_PARQUET_URL = "hf://datasets/Saksham4540/Telegram-DB/TG_DATA_PARTS/*/*.parquet"

@app.get("/")
def home():
    return {"status": "API Active", "endpoint": "/search?id=YOUR_ID"}

@app.get("/search")
def search_by_user_id(id: str = Query(..., description="Telegram User ID")):
    if not id.isdigit():
        raise HTTPException(status_code=400, detail="Invalid ID format")

    con = duckdb.connect()
    
    try:
        # hf:// protocol allow karne ke liye settings
        con.execute("SET allow_asterisks_in_http_paths = true;")
        
        sql = f"""
            SELECT 
                user_id, username, first_name, last_name, 
                phone, email, status, linked_id, linked_name, linked_handle
            FROM read_parquet('{HF_PARQUET_URL}')
            WHERE user_id = {int(id)}
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
