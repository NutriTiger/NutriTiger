# Based on https://github.com/shannon-heh/TigerSnatch/blob/main/app.py#L75
from sys import path
path.append('src')

from flask import Flask, render_template, request
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

def get_netid():

    # access database and get the netid that matches the CAS login
    return netid

#--------------------------------------------------------------------

@app.route('/', methods=['GET'])
@app.route('/index', methods=['GET'])
def index():
    # Add cookies? helper method for if this is first contact or returning
    return render_template('index.html')

#--------------------------------------------------------------------

@app.route('/homepage', methods=['GET'])
def homepage():
    return render_template('homepage.html', ampm=get_ampm(), netid=get_netid())

#--------------------------------------------------------------------

@app.route('/dhallmenus', methods=['GET'])
def dhall_menus():
    # Fetch menu data from database
    return render_template('dhallmenus.html')

#--------------------------------------------------------------------

@app.route('/firstcontact', methods=['POST'])
def first_contact():
    if request.method == 'POST':

        # Get value entered into the calorie goal box
        user_goal = request.form['line']

        # Process data here (add to db)
    return render_template('firstcontact.html')

#--------------------------------------------------------------------

@app.route('/settings', methods=['POST'])
def settings():

    # Update database with new input value
    new_user_goal = request.form['line']

    return render_template('settings.html')

#--------------------------------------------------------------------

@app.route('editingplate', methods=['POST'])
def editing_plate():
    return render_template('editingplate.html')

#--------------------------------------------------------------------

if __name__ == '__main__':
    app.run(host='localhost', port=5000, debug=True)
