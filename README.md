<br />
<div align="center">
    <img src="static/media/logo.png" alt="Logo" width="100" height="100">

  <h3 align="center">NutriTiger</h3>

  <p align="center">
    NutriTiger is a new upcoming web application that allows Princeton students to track nutritional information from the dining halls.</a>
    <br />
  </p>
</div>

  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#installation">Installation</a>
    </li>
    <li><a href="#contributing">Contributing</a></li>
  </ol>

## Installation
1. Clone the repository
```sh
   git clone https://github.com/NutriTiger/NutriTiger.git
```
2. Install all required packages
```sh
pip install -r requirements.txt
```
3. ``python app.py``
## Contributing
### Branching Guidelines
The general branch structure is as follows.
- ``main``
- ``prototype``
- ``alpha``
- ``beta``

Then, for stretch goals and other features, use the feature syntax
Ex: ``feature/webscraping``

Branching Commands:

Change to branch:
- ``git checkout feature/abc`` (equivalent to ``git branch feature/abc``)

Make edits/commit/push accordingly to your branch freely.

When you are ready to merge with prototype, or whatever master branch
- ``git checkout prototype``
- ``git merge feature/abc``
- Resolve any merge conflicts (can do visually)
- Commit changes ``git commit -m "Merging abc with prototype"``
- ``git push origin prototype`` (origin is the configured remote name)


Miscellaneous Commands
``python –m pip freeze > requirements.txt``
### Database Guidelines
The db files (under src) require a mongodb username and password with read and write access to connect to the database. 

If you are a collaborater of the NutriTiger project, you may create a username and password by accessing the NutriTiger project on MongoDB Atlas: 
- On the menu bar on the left hand side, click on "DataBase Access."
- Then, click on "Add New DataBase User" and create your username and password for "Password Authentication." Set your "Built-in Role" to be "Atlas admin." Finally, click "Add User." 

If you are not a collaborater of the NutriTiger project, you may acquire a username and password by contacting ________.

When you are ready to run any of the database files, make sure you have exported your mongodb username and password as environment variables with these commands in your terminal:
- ``export MONGODB_USERNAME=<username>``
- ``export MONGODB_PASSWORD=<password>``

Replace ``<username>`` and ``<password>`` with your mongodb username and password accordingly.

