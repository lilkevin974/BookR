import os
import requests

from flask import Flask, session, render_template, request, redirect, url_for, jsonify
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


@app.route("/", methods=["GET", "POST"])
def login():
    
    alert=request.args.get('alert',None)  
    if alert==None:       
        return render_template("login.html")
    return render_template("login.html", alert=alert)

@app.route("/register", methods=["GET", "POST"])
def register():
    
    if request.method == 'POST':
        username = request.form.get ("username")
        password = request.form.get ('password')

        db.execute("INSERT INTO users (username,password) VALUES (:username, :password)",
                {"username": username, "password":password})
        db.commit()

        return redirect( url_for ('login'))
     
    return render_template("register.html")

@app.route("/test", methods=["GET", "POST"])
def test():

    alert= "Please Log In"
    
    
    if request.method=='GET':
        if session.get('usern') is None:
            return redirect( url_for ('login', alert=alert))
        return render_template ("test.html", username= session['usern'])
    
    if session.get('usern') is None:
        session['usern']=''

    if request.method == 'POST' and "login" in request.form:
        usern = request.form.get ("username")
        session['usern']=usern
        passw = request.form.get ('password')

        log = db.execute ("SELECT * FROM users WHERE username = :username AND password = :password", {"username": usern, "password":passw}).fetchone()
        if log is not None:
            return render_template ("test.html", username= session['usern'])
          
        return redirect( url_for ('login', alert=alert))
    
    

    book = {"title":'', "isbn":'',"author":'',"year":''}

    if request.method == 'POST' and "search" in request.form:
        book['isbn']=request.form.get("isbn")
        book['title']=request.form.get("title")
        book['title']=book['title'].title()
        book['author']=request.form.get("author")
        book['year']= request.form.get("year")
       
        s= db.execute("SELECT * FROM books WHERE isbn = :isbn OR title =:title \
            OR author =:author OR year =:year LIMIT 30", \
            {"isbn":book['isbn'], "title":book['title'], "author":book['author'], "year":book['year']}).fetchall()

        c=db.execute("SELECT * FROM books WHERE isbn = :isbn OR title =:title \
            OR author =:author OR year =:year LIMIT 30", \
            {"isbn":book['isbn'], "title":book['title'], "author":book['author'], "year":book['year']}).rowcount

        print(c)
        print(session['usern'])  

        if s is not None:
            return render_template ("test.html", username= session['usern'], search=s, result =c)
        
        c=0
        return render_template ("test.html", username= session['usern'], search=s, result =c)
   
    return redirect( url_for ('login', alert=alert))  
        

@app.route("/profil/<int:bookpage>", methods=["GET", "POST"])
def profil(bookpage):
    
    

    book = db.execute("SELECT * FROM books WHERE id = :id", {"id": bookpage}).fetchone()
    
    
    res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "SOUMv8W4FhU0eHn267zg", "isbns":book.isbn })
    review_count=res.json()
    av_rate = review_count["books"][(0)]['average_rating']
    if av_rate is None:
        av_rate='-' 
    
    if request.method == 'POST' and "new-review" in request.form:
        db.execute("UPDATE ratings SET review = NULL WHERE books_id=:books_id AND username=:user_id", {"user_id": session['usern'], "books_id": bookpage})
        db.commit()

    review = db.execute("SELECT * FROM ratings WHERE books_id = :id AND review IS NOT NULL", {"id": bookpage}).fetchall()
    review_number=db.execute("SELECT * FROM ratings WHERE books_id = :id AND review IS NOT NULL", {"id": bookpage}).rowcount
    
    user_review=db.execute("SELECT * FROM ratings WHERE books_id = :id AND username=:user_id AND review IS NOT NULL AND rate is NOT NULl", {"id": bookpage, "user_id":session['usern'] }).fetchone()
    
    if user_review is not None:
        return render_template("bookpage_rate.html", book=book, rate=user_review.rate, av_rate=rate, review=review, review_number=review_number )


    if request.method == 'POST' and "submit-review" in request.form:
        text_review=request.form.get("text-review")
        db.execute("UPDATE ratings SET review=:review WHERE books_id=:books_id AND username=:user_id", {"user_id": session['usern'], "books_id": bookpage, "review": text_review})
        db.commit()
        review = db.execute("SELECT * FROM ratings WHERE books_id = :id AND review IS NOT NULL", {"id": bookpage}).fetchall()
        review_number=db.execute("SELECT * FROM ratings WHERE books_id = :id AND review IS NOT NULL", {"id": bookpage}).rowcount


    return render_template("bookpage.html", book=book, rate=av_rate, username= session['usern'], review=review, review_number=review_number)
    
@app.route("/profil/<int:bookpage>/<int:rating>")
def profil_rate(bookpage, rating):

    book = db.execute("SELECT * FROM books WHERE id = :id", {"id": bookpage}).fetchone()
    

    user_rate=db.execute("SELECT * FROM ratings WHERE username = :user_id AND books_id=:bookpage", {"user_id": session['usern'], "bookpage":bookpage}).fetchone()

    if user_rate is None:
        db.execute("INSERT INTO ratings (username, books_id) VALUES (:user_id, :books_id)",
              {"user_id": session['usern'], "books_id": bookpage})
        db.commit()

    user_rate=db.execute("SELECT * FROM ratings WHERE username = :user_id AND books_id=:bookpage", {"user_id": session['usern'], "bookpage":bookpage}).fetchone()

    db.execute("UPDATE ratings SET rate=:rate WHERE id=:id", {"rate":rating, "id":user_rate.id})
    db.commit()
    
    res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "SOUMv8W4FhU0eHn267zg", "isbns":book.isbn })
    review_count=res.json()
    av_rate = review_count["books"][(0)]['average_rating']
    if av_rate is None:
        av_rate='-'

    review = db.execute("SELECT * FROM ratings WHERE books_id = :id AND review IS NOT NULL", {"id": bookpage}).fetchall()
    review_number=db.execute("SELECT * FROM ratings WHERE books_id = :id AND review IS NOT NULL", {"id": bookpage}).rowcount
    rate_number=db.execute("SELECT * FROM ratings WHERE books_id = :id AND rate IS NOT NULL", {"id": bookpage}).rowcount

    ratings_count = review_count["books"][(0)]['work_ratings_count']
    ratings_count=ratings_count + rate_number
    if ratings_count is None:
        ratings_count='-'

    return render_template("bookpage_rate.html", book=book, rate=rating, av_rate=av_rate, review=review, review_number=review_number, rate_number=ratings_count)

@app.route("/api/<isbn>")
def api(isbn):

    book=db.execute("SELECT * FROM books WHERE isbn=:isbn", {"isbn":isbn}).fetchone()
    rating=db.execute("SELECT * FROM ratings WHERE books_id=:book_id", {"book_id":book.id}).rowcount
    
    av_rate = db.execute("SELECT AVG (rate) FROM ratings WHERE books_id=:id", {"id": book.id}).fetchall()
    for i in av_rate:
        if i[0] is not None:
            av_rate=float(i[0]) 
        else:
            av_rate='-' 

    if book is None:
        return jsonify({"error": "ISBN number doesn't exist"}), 404
    
    return jsonify({
    "title": book.title,
    "author": book.author,
    "year": book.year,
    "isbn": book.isbn,
    "review_count": rating,
    "average_score": av_rate
    })

@app.route("/logout")
def logout():
    session.pop('usern')
    alert="Logout Successful"

    return redirect( url_for ('login', alert=alert)) 

        

