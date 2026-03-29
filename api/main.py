from fastapi import FastAPI
from api.webhook_handler import router as webhook_router

app = FastAPI(title="Intelligent RevOps Agent API")

app.include_router(webhook_router, prefix="/webhooks", tags=["webhooks"])

@app.get("/health")
async def health_check():
    return {"status": "operational", "agent_version": "1.0.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
