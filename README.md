# Project 1 - CS50W

Web application using Flask and PostgreSQL Database
The user of the website can create an account with a username and a password which are stored in a database.
Then he can log in into the website and get to webpage where he can search book by typing differents informations.
He can select a book in the different results and get to page where he can see details about the book and submit a review and a rating and those of the other users.
He can finally log out of the website.

---

Templates folder contains different html files :

*register.html : where the user can register;
*login.html : where the user can log in, once registered;
*base.html : layout for the previous pages;
*test.html : where the user can search for a book by typing in isbn, title, author or year of the book;
*bookpage.html : where the user can see book details and submit rating or/and review ;
*boopage_rate.html : where the user can see his own rating info for the book and submit a new review.

---

Static folder contains:
*Images folder which contains two .jpg files used for styling background 
*Style folder:
    *Sass 
    *CSS map
    *CSS

---

-application.py : python web application using Flask and Sqlalchemy
-books.csv : spreadsheet in CSV format of 5000 different books
-import.py : python app to import tables that our flask application need to run
-requirements.txt : python packages that need to be installed