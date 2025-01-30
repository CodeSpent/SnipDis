
import os
import uvicorn
from fastapi import FastAPI, HTTPException, Request
from bot import bot

app = FastAPI()

from dotenv import load_dotenv
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN environment variable is not set!")

@app.get("/")
async def root():
    return {"status": "ok"}

@app.post("/discord")
async def discord_interactions(request: Request):
    try:
        body = await request.json()
        # Pass the interaction to the bot handler
        response = bot.handle_interaction(body)  # You'll need to implement this in your bot
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error handling Discord interaction: {e}")


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000)  # Main is the name of this file
