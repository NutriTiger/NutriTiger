# ----------------------------------------------------------------------
# 
# app.py
#
# ----------------------------------------------------------------------

# Based on https://github.com/shannon-heh/TigerSnatch/blob/main/app.py#L75
from sys import path
path.append('src')

from flask import Flask, render_template, request, redirect
import time
from CASClient import CASClient

#--------------------------------------------------------------------

app = Flask(__name__)
_cas = CASClient()

#--------------------------------------------------------------------

# Code used from PennyFlaskJinja/penny.py from Lecture 10
def get_ampm():
    current_hr = int(time.strftime('%I'))
    am_pm = time.strftime('%p')
    if am_pm == "AM":
        return 'morning'
    elif am_pm == "PM" and current_hr < 6:
        return 'afternoon'
    return 'evening'

#--------------------------------------------------------------------

@app.route('/', methods=['GET'])
@app.route('/index', methods=['GET'])
def index():
    # Check if it is a user's first visit
    visited_before = request.cookies.get('visited_before')
    if 'visited_before' is None:
        # indicate first contact
        visited_before = '(None)'
        # Redirect to set initial goals page
        return redirect('/welcome')
    return render_template('index.html')

#--------------------------------------------------------------------

@app.route('/homepage', methods=['GET'])
def homepage():
    netid = _cas.authenticate()
    netid = netid.rstrip()
    return render_template('homepage.html', ampm=get_ampm(), netid=netid)

#--------------------------------------------------------------------

@app.route('/dhallmenus', methods=['GET'])
def dhall_menus():
    # Fetch menu data from database
    return render_template('dhallmenus.html')

#--------------------------------------------------------------------

@app.route('/welcome', methods=['POST'])
def first_contact():
    if request.method == 'POST':

        # Get value entered into the calorie goal box
        user_goal = request.form['line']

        # Validate value
        # Store value into database

    return render_template('firstcontact.html')

#--------------------------------------------------------------------

@app.route('/settings', methods=['POST'])
def settings():
    if request.method == 'POST':
        # Update database with new input value
        new_user_goal = request.form['line']

        # Validate value
        # Store value into database

    return render_template('settings.html')

#--------------------------------------------------------------------

@app.route('/editingplate', methods=['POST'])
def editing_plate():
    return render_template('editingplate.html')

#--------------------------------------------------------------------

if __name__ == '__main__':
    app.run(host='localhost', port=5000, debug=True)
