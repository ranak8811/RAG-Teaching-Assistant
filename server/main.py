from fastapi import FastAPI
from server.auth.route import router as auth_router

app = FastAPI()

app.include_router(auth_router)

@app.get('/')
def home():
    return {"message": "Hello World"}
