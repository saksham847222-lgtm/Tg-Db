from fastapi import FastAPI, Query, HTTPException
import duckdb

app = FastAPI(
    title="Telegram DB Search API",
    description="Search Telegram User Details from Hugging Face Parquet Dataset"
)

# Remote Hugging Face Parquet Files Pattern
HF_PARQUET_URL = "https://huggingface.co/datasets/Saksham4540/Telegram-DB/resolve/main/TG_DATA_PARTS/*/*.parquet"

@app.get("/")
def home():
    return {
        "status": "API is Active",
        "usage": "/search?id=1646744189"
    }

@app.get("/search")
def search_by_user_id(id: str = Query(..., description="Telegram User ID (e.g., 1646744189)")):
    # Basic Validation: ID digits hi honi chahiye
    if not id.isdigit():
        raise HTTPException(
            status_code=400, 
            detail="Invalid Telegram ID format. ID must contain digits only."
        )

    con = duckdb.connect()
    
    try:
        # Wildcards (*) via HTTP allow karne ke liye DuckDB setting
        con.execute("SET allow_asterisks_in_http_paths = true;")
        
        # Exact column 'user_id' se match karne ke liye query
        sql = f"""
            SELECT 
                user_id,
                username,
                first_name,
                last_name,
                phone,
                email,
                status,
                linked_id,
                linked_name,
                linked_handle
            FROM read_parquet('{HF_PARQUET_URL}')
            WHERE user_id = {int(id)}
        """
        
        # Execution & DF to Dict conversion
        df_result = con.execute(sql).df()
        con.close()
        
        results = df_result.to_dict(orient="records")
        
        return {
            "status": "success",
            "query_id": id,
            "count": len(results),
            "data": results
        }
    except Exception as e:
        con.close()
        return {
            "status": "error",
            "message": str(e)
        }
