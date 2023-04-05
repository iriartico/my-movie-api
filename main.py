from fastapi import FastAPI, Body, Path, Query
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field
from typing import Optional
app = FastAPI()
app.title = "My app with FastAPI"
app.version = "0.0.1"


class Movie(BaseModel):
    id: Optional[int] = None
    title: str = Field(min_length=5, max_length=15)
    overview: str = Field(min_length=15, max_length=50)
    year: int = Field(le=2022)
    # ge = mayor o igual && le = menor o igual
    rating: float = Field(ge=1, le=10)
    category: str = Field(min_length=5, max_length=15)

    class Config:
        schema_extra = {
            "example": {
                "id": 1,
                "title": "My movie",
                "overview": "Description of the movie",
                "year": 2022,
                "rating": 5.5,
                "category": "Action"
            }
        }


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
def get_movie(id: int = Path(ge=1, le=2000)):
    movie = list(filter(lambda x: x['id'] == id, movies))
    return movie[0] if len(movie) > 0 else "Nothing to show"


@app.get('/movies/', tags=['movies'])
def get_movies_by_category(category: str = Query(min_length=5, max_length=15)):
    movies_by_category = list(
        filter(lambda x: x['category'] == category, movies))
    return movies_by_category if len(movies_by_category) > 0 else "Nothing to show"


@app.post('/movies', tags=['movies'])
def create_movie(movie: Movie):
    movies.append(movie)
    return movies


@app.put('/movies/{id}', tags=['movies'])
def update_movie(id: int, movie: Movie):
    for item in movies:
        if item['id'] == id:
            item['title'] = movie.title
            item['overview'] = movie.overview
            item['year'] = movie.year
            item['rating'] = movie.rating
            item['category'] = movie.category
        return movies


@app.delete('/movies/{id}', tags=['movies'])
def remove_movie(id: int):
    for item in movies:
        if item['id'] == id:
            movies.remove(item)
            return movies
        else:
            return 'Movie not found'
