from movie_database import get_movie


TMDB_API_KEY='f9308956ba6a4d89c9739a1dc67b81dd'
db_config = {
"host": "127.0.0.1", 
"database": "film",
"user": "postgres",
"password": "secret123"
}

get_movie([1213], db_config, TMDB_API_KEY)