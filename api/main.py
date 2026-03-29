from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.webhook_handler import router as webhook_router
from api.frontend_handler import router as frontend_router

app = FastAPI(title="Intelligent RevOps Agent API")

# Setup CORS for the HTML prototype file to bypass cross-origin restrictions
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(webhook_router, prefix="/webhooks", tags=["webhooks"])
app.include_router(frontend_router, prefix="/api", tags=["frontend"])

from fastapi.responses import RedirectResponse

@app.get("/")
async def root_redirect():
    # Instantly redirects localhost:8000 over to the Swagger UI page!
    return RedirectResponse(url="/docs")

@app.get("/health")
async def health_check():
    return {"status": "operational", "agent_version": "1.0.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
