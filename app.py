import string
import random
from flask import Flask, request, redirect, url_for, render_template

app = Flask(__name__)

uppers = string.ascii_uppercase
lowers = string.ascii_lowercase
digits = string.digits
chars = uppers + lowers + digits
root_url = "localhost:5000/"

url_dict = {"empty" : {"url" : "empty", "views" : 0}}

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
    if key in url_dict:
        url_dict[key]["views"] += 1
        return redirect("http://" + url_dict[key]["url"])

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
    url_dict[key] = {"url" : long_url, "views" : 0}
    return root_url + key

# generates a random string form the ascii set
def get_random_string(size = 6, chars = chars):
    return ''.join(random.choice(chars) for _ in range(size))

if __name__ == '__main__':
    app.run()
    app.debug = True
