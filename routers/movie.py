from fastapi import APIRouter, Path, Query, Depends
from fastapi.responses import JSONResponse
from config.database import Session
from models.movie import Movie as MovieModel
from fastapi.encoders import jsonable_encoder
from middlewares.jwt_bearer import JWTBearer
from services.movie import MovieService
from schemas.movie import Movie

movie_router = APIRouter()


# @movie_router.get('/movies', tags=['movies'], status_code=200)
@movie_router.get('/movies', tags=['movies'], status_code=200, dependencies=[Depends(JWTBearer())])
def get_movies():
    db = Session()
    response = MovieService(db).get_movies()
    return JSONResponse(status_code=200, content=jsonable_encoder(response))


@movie_router.get('/movies/{id}', tags=['movies'])
def get_movie(id: int = Path(ge=1, le=2000)):
    db = Session()
    response = MovieService(db).get_movie(id)
    if not response:
        return JSONResponse(status_code=404, content={"message": "Movie not found"})

    return JSONResponse(status_code=200, content=jsonable_encoder(response))


@movie_router.get('/movies/', tags=['movies'], status_code=200)
def get_movies_by_category(category: str = Query(min_length=5, max_length=15)):
    db = Session()
    response = MovieService(db).get_movies_by_category(category)
    if not response:
        return JSONResponse(status_code=404, content={"message": "The category does not exist"})

    return JSONResponse(status_code=200, content=jsonable_encoder(response))


@movie_router.post('/movies', tags=['movies'], status_code=201)
def create_movie(movie: Movie):
    db = Session()
    MovieService(db).create_movie(movie)
    return JSONResponse(status_code=201, content={"message": "Movie registered"})


@movie_router.put('/movies/{id}', tags=['movies'], status_code=200)
def update_movie(id: int, movie: Movie):
    db = Session()
    response = MovieService(db).get_movie(id)
    if not response:
        return JSONResponse(status_code=404, content={"message": "Movie not found"})

    MovieService(db).update_movie(id, movie)
    return JSONResponse(status_code=200, content={"message": "Movie updated"})


@movie_router.delete('/movies/{id}', tags=['movies'], status_code=200)
def remove_movie(id: int):
    db = Session()
    response = MovieService(db).get_movie(id)
    if not response:
        return JSONResponse(status_code=404, content={"message": "Movie not found"})

    MovieService(db).delete_movie(id)
    return JSONResponse(status_code=200, content={"message": "Movie deleted"})
