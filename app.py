import string
import random
import sqlite3
from flask import Flask, request, redirect, url_for, render_template, g

app = Flask(__name__)

# this string is used to generate the random keys for short urls
uppers = string.ascii_uppercase
lowers = string.ascii_lowercase
digits = string.digits
chars = uppers + lowers + digits

# the root directory of whatever site the app is hosted on
root_url = "immense-plateau-4380.herokuapp.com/"

# url_dict = {"empty" : {"url" : "empty", "views" : 0}}

"""
This is all the database stuff, maybe should move to a models.py file?
"""
DATABASE = 'database.db'

def insert_url(key,url,views):
    con = get_db()
    cur = con.cursor()
    print cur.execute("INSERT INTO entries (key,url,views) VALUES (?,?,?)", (key,url,views))
    con.commit()
    con.close()

def update_views(key):
    con = get_db()
    cur = con.cursor()
    cur.execute("UPDATE entries SET views = views + 1 WHERE key=?", [key])
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
        db.row_factory = sqlite3.Row
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

"""
All of the routes and python functions
"""
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
    update_views(key)
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

# returns all of the urls in the database
@app.route("/get-all-urls")
def get_all_urls():
    url_list = []
    for entry in query_db('select * from entries'):
        url_list.append([entry['url'], 'with the key', entry['key'], 'has been viewed', entry['views'], 'times'])
    #urls = query_db('select * from entries).encode('ascii')
    return str(url_list)

# renders the form that asks the user for a url
def show_url_form():
    return render_template('url.html')

def show_short_url(long_url, short_url):
    return render_template('url.html', long_url=long_url, short_url=short_url)

# this is the function that shortens the url
def shorten_url(long_url):
    key = ""
    try:
        key = get_random_string()
        insert_url(key, long_url, 0)
    except:
        shorten_url(long_url)
    else:
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
