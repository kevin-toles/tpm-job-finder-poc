from src.error_service.handler import handle_error
from src.logging_service.logger import CentralLogger
"""
Health check endpoint for service liveness monitoring.
"""
from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI()
logger = CentralLogger()

@app.get("/health")
def health():
    # Stub health check logic
    status = "ok"  # Replace with actual health check logic if available
    logger.info(f"Health check status: {status}")
    return JSONResponse({"status": status})
        return JSONResponse({"status": "error"})

# For WSGI/ASGI servers
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
