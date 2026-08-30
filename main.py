from fastapi import FastAPI, Query, HTTPException
import duckdb

app = FastAPI(title="Telegram DB Search API")

# Hugging Face Public Parquet Files URL Pattern
# TG_DATA_PARTS folder ke andar jitne bhi part_id folders hain, ye sabhi ko read kar lega
HF_PARQUET_URL = "https://huggingface.co/datasets/Saksham4540/Telegram-DB/resolve/main/TG_DATA_PARTS/*/*.parquet"

@app.get("/")
def home():
    return {"status": "API Active", "endpoint": "/search?id=YOUR_10_DIGIT_ID"}

@app.get("/search")
def search_by_id(id: str = Query(..., description="10-digit Telegram User ID")):
    # 10-digit check validation
    if not id.isdigit() or len(id) != 10:
        raise HTTPException(
            status_code=400, 
            detail="Invalid ID format. Please provide a valid 10-digit Telegram ID."
        )

    con = duckdb.connect()
    
    # Remote Parquet Querying via DuckDB
    # Note: Agar parquet file me ID ka column name alag hai (e.g. 'user_id' ya 'telegram_id'), 
    # to neeche 'id' ki jagah us column name ko update kar dein.
    sql = f"""
        SELECT * 
        FROM read_parquet('{HF_PARQUET_URL}')
        WHERE CAST(id AS VARCHAR) = '{id}'
    """
    
    try:
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
