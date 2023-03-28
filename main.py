from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI()
app.title = "My app with FastAPI"
app.version = "0.0.1"


movies = [
    {
        'id': 1,
        'title': 'Avatar',
        'overview': "En un exuberante planeta llamado Pandora viven los Na'vi, seres que ...",
        'year': 2009,
        'rating': 7.8,
        'category': 'Acción'
    },
    {
        'id': 2,
        'title': 'Avatar 2',
        'overview': "En un exuberante planeta llamado Pandora viven los Na'vi, cotinuan con ...",
        'year': 2022,
        'rating': 7.1,
        'category': 'Acción'
    }
]


@app.get('/', tags=['home'])
def home():
    return HTMLResponse('<h1>Home Page</h1>')


@app.get('/movies', tags=['movies'])
def get_movies():
    return movies


@app.get('/movies/{id}', tags=['movies'])
def get_movie(id: int):
    movie = list(filter(lambda x: x['id'] == id, movies))
    return movie[0] if len(movie) > 0 else "Nothing to show"


@app.get('/movies/', tags=['movies'])
def get_movies_by_category(category: str, year: int):
    movies_by_category = list(filter(lambda x: x['category'] == category and x['year'] == year, movies))
    return movies_by_category if len(movies_by_category) > 0 else "Nothing to show"
