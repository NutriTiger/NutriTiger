# Based on https://github.com/shannon-heh/TigerSnatch/blob/main/app.py#L75
from sys import path
path.append('src')

from flask import Flask, render_template
from CASClient import CASClient

app = Flask(__name__)
_cas = CASClient()


@app.route('/')
def hello_world():
    #print("HERE!")
    #netid = _cas.authenticate()
    #print(netid)
    #netid = netid.rstrip()
    return render_template('dhallmenus.html')

if __name__ == '__main__':
    app.run(host='localhost', port=5000, debug=True)
