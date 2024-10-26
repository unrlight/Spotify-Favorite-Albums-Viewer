from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from spotipy import oauth2
import spotipy
import uvicorn
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI()
templates = Jinja2Templates(directory="templates")

CLIENT_ID = os.environ.get("client_id")
CLIENT_SECRET = os.environ.get("client_secret")
REDIRECT_URI = 'http://localhost:8005/callback'
SCOPE = 'user-library-read'

sp_oauth = oauth2.SpotifyOAuth(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    redirect_uri=REDIRECT_URI,
    scope=SCOPE
)

@app.get("/")
def login():
    auth_url = sp_oauth.get_authorize_url()
    return RedirectResponse(auth_url)

@app.get("/callback")
def callback(request: Request, code: str):
    token_info = sp_oauth.get_access_token(code)
    access_token = token_info['access_token']
    sp = spotipy.Spotify(auth=access_token)

    results = sp.current_user_saved_albums(limit=50)
    albums = []
    while results:
        for item in results['items']:
            album = item['album']
            albums.append({
                'name': album['name'],
                'artist': album['artists'][0]['name'],
                'image': album['images'][0]['url'] if album['images'] else None,
                'url': album['external_urls']['spotify']
            })
        if results['next']:
            results = sp.next(results)
        else:
            break

    return templates.TemplateResponse("albums.html", {"request": request, "albums": albums})

if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8005)
