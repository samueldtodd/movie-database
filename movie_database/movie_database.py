import psycopg2
import requests
import json
from psycopg2 import OperationalError

class Database:
    def __init__(self, config):
        self.config = config
        self.conn = self.connect()

    def connect(self):

        try:
            conn = psycopg2.connect(
                host=self.config['host'],
                dbname=self.config['database'],
                user=self.config['user'],
                password=self.config['password']
            )
            return conn

        except OperationalError as e:
            print(f"❌ Database connection failed: {e}")
            raise


def get_movie(ids, db_config, api_key):

    db_conn = Database(db_config).connect()
    
    results = []

    for movie_id in ids:
            
        data = get_from_db(movie_id, db_conn)

        if not data:
            print("❌ Not found in DB, calling TMDB")
            data = get_from_tmdb(movie_id, api_key)
            save_to_db(movie_id, data['data'], db_conn)

        results.append({
            "poster_url": data["poster_url"],
            "title": data["title"]
        })

    return results

def get_from_db(movie_id, db_conn):
    
    cur = db_conn.cursor()

    # 🔎 1️⃣ Check database first
    cur.execute("SELECT title, poster_url FROM movies WHERE id = %s", (movie_id,))
    result = cur.fetchone()

    if result and result[0]:
        print("✅ Found in database")
        return {
            "poster_url": "https://image.tmdb.org/t/p/w500" + result[1],
            "title": result[0]
        }
    
def get_from_tmdb(movie_id, api_key):
    search_url = f"https://api.themoviedb.org/3/movie/{movie_id}?append_to_response=credits"
    params = {
        "api_key": api_key,
        "query": movie_id
    }

    response = requests.get(search_url, params=params)
    data = response.json()

    return {
            "poster_url": "https://image.tmdb.org/t/p/w500" + data["poster_path"],
            "title": data["title"],
            "data": data
    }
        

def save_to_db(movie_id, data, db_conn):
        
    cur = db_conn.cursor()

    cur.execute(
        "INSERT INTO movies (id, title, poster_url, details) VALUES (%s, %s, %s, %s)",
        (movie_id, data['title'], data["poster_path"], json.dumps(data))
    )
    db_conn.commit()

