from fastapi import APIRouter, Path, Query, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Optional
from config.database import Session
from models.movie import Movie as MovieModel
from fastapi.encoders import jsonable_encoder
from middlewares.jwt_bearer import JWTBearer


movie_router = APIRouter()


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


# @movie_router.get('/movies', tags=['movies'], status_code=200)
@movie_router.get('/movies', tags=['movies'], status_code=200, dependencies=[Depends(JWTBearer())])
def get_movies() -> list[Movie]:
    db = Session()
    response = db.query(MovieModel).all()
    return JSONResponse(status_code=200, content=jsonable_encoder(response))


@movie_router.get('/movies/{id}', tags=['movies'])
def get_movie(id: int = Path(ge=1, le=2000)):
    db = Session()
    response = db.query(MovieModel).filter(MovieModel.id == id).first()
    if not response:
        return JSONResponse(status_code=404, content={"message": "Movie not found"})

    return JSONResponse(status_code=200, content=jsonable_encoder(response))


@movie_router.get('/movies/', tags=['movies'], status_code=200)
def get_movies_by_category(category: str = Query(min_length=5, max_length=15)):
    db = Session()
    response = db.query(MovieModel).filter(
        MovieModel.category == category).all()
    if not response:
        return JSONResponse(status_code=404, content={"message": "The category does not exist"})

    return JSONResponse(status_code=200, content=jsonable_encoder(response))


@movie_router.post('/movies', tags=['movies'], status_code=201)
def create_movie(movie: Movie):
    db = Session()
    new_movie = MovieModel(**movie.dict())
    db.add(new_movie)
    db.commit()
    return JSONResponse(status_code=201, content={"message": "Movie registered"})


@movie_router.put('/movies/{id}', tags=['movies'], status_code=200)
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


@movie_router.delete('/movies/{id}', tags=['movies'], status_code=200)
def remove_movie(id: int):
    db = Session()
    response = db.query(MovieModel).filter(MovieModel.id == id).first()
    if not response:
        return JSONResponse(status_code=404, content={"message": "Movie not found"})

    db.delete(response)
    db.commit()
    return JSONResponse(status_code=200, content={"message": "Movie deleted"})
