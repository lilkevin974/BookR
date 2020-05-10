import os
import csv

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine(os.getenv("DATABASE_URL")) 
db = scoped_session(sessionmaker(bind=engine))

db.execute("CREATE TABLE IF NOT EXISTS books(id SERIAL PRIMARY KEY, isbn VARCHAR NOT NULL,title VARCHAR NOT NULL,author VARCHAR NOT NULL, year INTEGER NOT NULL)")
db.execute("CREATE TABLE IF NOT EXISTS users (id SERIAL PRIMARY KEY, username VARCHAR UNIQUE NOT NULL, password VARCHAR NOT NULL)")
db.execute("CREATE TABLE IF NOT EXISTS ratings(id SERIAL PRIMARY KEY, rate INTEGER, review VARCHAR, books_id INTEGER REFERENCES books, username VARCHAR REFERENCES users (username))")

db.commit()

b = open("books.csv")
reader = csv.reader(b)

next(reader, None)
for isbn, title, author, year in reader:
    db.execute("INSERT INTO books (isbn, title, author, year) VALUES (:isbn, :title, :author, :year)",
            {"isbn": isbn, "title": title, "author": author, "year": year})
db.commit()