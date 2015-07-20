import string
import random
import sqlite3
from flask import Flask, request, redirect, url_for, render_template, g

app = Flask(__name__)

uppers = string.ascii_uppercase
lowers = string.ascii_lowercase
digits = string.digits
chars = uppers + lowers + digits
root_url = "localhost:5000/"
url_dict = {"empty" : {"url" : "empty", "views" : 0}}

DATABASE = 'database.db'

def insert_url(key,url,views):
    con = get_db()
    cur = con.cursor()
    cur.execute("INSERT INTO entries (key,url,views) VALUES (?,?,?)", (key,url,views))
    con.commit()
    con.close()

def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

def connect_to_database():
    return sqlite3.connect(DATABASE)

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = connect_to_database()
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

@app.route('/')
def index():
    return redirect(url_for('url'))

@app.route('/url', methods=['GET', 'POST'])
def url():
    if request.method == 'GET':
        return show_url_form()
    elif request.method == 'POST':
        long_url = request.form['long-url']
        short_url = shorten_url(long_url)
        return show_short_url(long_url, short_url)

# uses the key to redirect to the long url
@app.route("/<key>")
def get_page(key):
    url = query_db('select url from entries where key = ?',[key], one=True)[0].encode('ascii')
    # if key in url_dict:
    #     url_dict[key]["views"] += 1
    return redirect("http://" + url)

# returns the short url as data for loading in the background
@app.route("/get-short-url/", methods=['GET', 'POST'])
def get_short_url():
    if request.method == 'GET':
        return show_url_form()
    elif request.method == 'POST':
        long_url = request.data
        short_url = shorten_url(long_url)
        return short_url

# renders the form that asks the user for a url
def show_url_form():
    return render_template('url.html')

def show_short_url(long_url, short_url):
    return render_template('url.html', long_url=long_url, short_url=short_url)

# this is the function that shortens the url
def shorten_url(long_url):
    key = "empty"
    while key in url_dict:
        key = get_random_string()
    #url_dict[key] = {"url" : long_url, "views" : 0}
    insert_url(key, long_url, 0)
    return root_url + key

# generates a random string form the ascii set
def get_random_string(size = 6, chars = chars):
    return ''.join(random.choice(chars) for _ in range(size))

if __name__ == '__main__':
    with app.app_context():
    # within this block, current_app points to app.
        print query_db('select * from entries')
    app.run()
    app.debug = True
