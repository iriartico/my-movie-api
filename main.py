from fastapi import FastAPI, Body, Path, Query, Request, HTTPException, Depends
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel, Field
from typing import Optional
from jwt_manager import create_token, validate_token
from fastapi.security import HTTPBearer
from config.database import Session, engine, Base
from models.movie import Movie as MovieModel
from fastapi.encoders import jsonable_encoder


app = FastAPI()
app.title = "My app with FastAPI"
app.version = "0.0.1"

Base.metadata.create_all(bind=engine)


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


@app.get('/', tags=['home'])
def home():
    return HTMLResponse('<h1>Home Page</h1>')


@app.post('/login', tags=['auth'])
def login(user: User):
    if user.email == "admin@email.com" and user.password == "admin123":
        token: str = create_token(user.dict())
    return JSONResponse(status_code=200, content=token)


@app.get('/movies', tags=['movies'], status_code=200)
# @app.get('/movies', tags=['movies'], status_code=200, dependencies=[Depends(JWTBearer())])
def get_movies() -> list[Movie]:
    db = Session()
    response = db.query(MovieModel).all()
    return JSONResponse(status_code=200, content=jsonable_encoder(response))


@app.get('/movies/{id}', tags=['movies'])
def get_movie(id: int = Path(ge=1, le=2000)):
    db = Session()
    response = db.query(MovieModel).filter(MovieModel.id == id).first()
    if not response:
        return JSONResponse(status_code=404, content={"message": "Movie not found"})

    return JSONResponse(status_code=200, content=jsonable_encoder(response))


@app.get('/movies/', tags=['movies'], status_code=200)
def get_movies_by_category(category: str = Query(min_length=5, max_length=15)):
    db = Session()
    response = db.query(MovieModel).filter(MovieModel.category == category).all()
    if not response:
        return JSONResponse(status_code=404, content={"message": "The category does not exist"})

    return JSONResponse(status_code=200, content=jsonable_encoder(response))


@app.post('/movies', tags=['movies'], status_code=201)
def create_movie(movie: Movie):
    db = Session()
    new_movie = MovieModel(**movie.dict())
    db.add(new_movie)
    db.commit()
    return JSONResponse(status_code=201, content={"message": "Movie registered"})


@app.put('/movies/{id}', tags=['movies'], status_code=200)
def update_movie(id: int, movie: Movie):
    db = Session()
    response = db.query(MovieModel).filter(MovieModel.id == id).first()
    if not response:
        return JSONResponse(status_code=404, content={"message": "Movie not found"})

    response.title = movie.title
    response.overview = movie.overview
    response.year = movie.year
    response.rating = movie.rating
    response.category = movie.category
    db.commit()
    return JSONResponse(status_code=200, content={"message": "Movie updated"})


@app.delete('/movies/{id}', tags=['movies'], status_code=200)
def remove_movie(id: int):
    db = Session()
    response = db.query(MovieModel).filter(MovieModel.id == id).first()
    if not response:
        return JSONResponse(status_code=404, content={"message": "Movie not found"})

    db.delete(response)
    db.commit()
    return JSONResponse(status_code=200, content={"message": "Movie deleted"})
