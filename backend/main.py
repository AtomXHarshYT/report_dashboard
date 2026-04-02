from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import auth, tickets

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://report-dashboard-eight.vercel.app/"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(tickets.router)