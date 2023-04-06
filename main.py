from fastapi import FastAPI, Body, Path, Query, Request, HTTPException, Depends
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel, Field
from typing import Optional
from jwt_manager import create_token, validate_token
from fastapi.security import HTTPBearer


app = FastAPI()
app.title = "My app with FastAPI"
app.version = "0.0.1"


class JWTBearer(HTTPBearer):
    async def __call__(self, request: Request):
        auth = await super().__call__(request)
        data = validate_token(auth.credentials)
        if data['email'] != "admin@email.com":
            raise HTTPException(status_code=403, detail="Invalid credentials")


class User(BaseModel):
    email: str
    password: str


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


@app.post('/login', tags=['auth'])
def login(user: User):
    if user.email == "admin@email.com" and user.password == "admin123":
        token: str = create_token(user.dict())
    return JSONResponse(status_code=200, content=token)


@app.get('/movies', tags=['movies'], status_code=200, dependencies=[Depends(JWTBearer())])
def get_movies() -> list[Movie]:
    return JSONResponse(status_code=200, content=movies)


@app.get('/movies/{id}', tags=['movies'])
def get_movie(id: int = Path(ge=1, le=2000)):
    movie = list(filter(lambda x: x['id'] == id, movies))
    return movie[0] if len(movie) > 0 else "Nothing to show"


@app.get('/movies/', tags=['movies'], status_code=200)
def get_movies_by_category(category: str = Query(min_length=5, max_length=15)):
    movies_by_category = list(
        filter(lambda x: x['category'] == category, movies))
    return JSONResponse(content=movies_by_category) if len(movies_by_category) > 0 else "Nothing to show"


@app.post('/movies', tags=['movies'], status_code=201)
def create_movie(movie: Movie):
    movies.append(movie)
    return JSONResponse(status_code=201, content={"message": "Movie registered"})


@app.put('/movies/{id}', tags=['movies'], status_code=200)
def update_movie(id: int, movie: Movie):
    for item in movies:
        if item['id'] == id:
            item['title'] = movie.title
            item['overview'] = movie.overview
            item['year'] = movie.year
            item['rating'] = movie.rating
            item['category'] = movie.category
        return JSONResponse(status_code=200, content={"message": "Movie updated"})


@app.delete('/movies/{id}', tags=['movies'], status_code=200)
def remove_movie(id: int):
    for item in movies:
        if item['id'] == id:
            movies.remove(item)
            return JSONResponse(status_code=200, content={"message": "Movie deleted"})
        else:
            return JSONResponse(status_code=404, content={"message": "Movie not found"})
