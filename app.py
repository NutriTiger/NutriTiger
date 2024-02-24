# Based on https://github.com/shannon-heh/TigerSnatch/blob/main/app.py#L75
from sys import path
path.append('src')

from flask import Flask
from CASClient import CASClient

app = Flask(__name__)
_cas = CASClient()


@app.route('/')
def hello_world():
    print("HERE!")
    netid = _cas.authenticate()
    print(netid)
    netid = netid.rstrip()
    return 'Hello, World!'

if __name__ == '__main__':
    app.run(host='localhost', port=5000, debug=True)
