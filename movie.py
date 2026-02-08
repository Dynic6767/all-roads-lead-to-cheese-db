import sqlite3

conn = sqlite3.connect('movies.db')  
cursor = conn.cursor()

cursor.execute("SELECT title, budget FROM movies ORDER BY vote_average DESC LIMIT 1;")
popular_movie = cursor.fetchone()
if popular_movie:
    print(f"Самый популярный фильм: {popular_movie[0]}, Бюджет: {popular_movie[1]}")

cursor.execute("SELECT title FROM movies WHERE release_date BETWEEN '2009-12-01' AND '2009-12-31' ORDER BY budget DESC LIMIT 1;")
expensive_movie = cursor.fetchone()
if expensive_movie:
    print(f"Самый дорогой фильм в декабре 2009 года: {expensive_movie[0]}")

cursor.execute("SELECT title FROM movies WHERE title LIKE 'The battle within%';")
slogan_movie = cursor.fetchone()
if slogan_movie:
    print(f"Фильм со слоганом 'The battle within.': {slogan_movie[0]}")
else:
    print('нету')
cursor.execute("SELECT title FROM movies WHERE release_date < '1980-01-01' AND vote_average > 8 ORDER BY vote_average DESC LIMIT 1;")
high_rated_movie = cursor.fetchone()
if high_rated_movie:
    print(f"Фильм до 1980 года с рейтингом выше 8: {high_rated_movie[0]}")

conn.close()