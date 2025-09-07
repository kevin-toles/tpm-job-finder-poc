"""
Health check endpoint for service liveness monitoring.
"""
from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI()

@app.get("/health")
def health():
    return JSONResponse({"status": "ok"})

# For WSGI/ASGI servers
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
