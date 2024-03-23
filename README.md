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
2. Install all required packages and python (version 3.11.7)
```sh
pip install -r requirements.txt
```
3. Configure .env file with tokens/secrets for the database

4. ``python app.py``
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


When you are ready to bring your branch up to date with main...
- ``git checkout feature/frontend``
- ``git pull origin main`` (this will bring any new changes to your branch)
- ``git push`` (now no longer "40 commits behind main")

When you are wanting to merge with main.
- ``git checkout main``
- ``git merge feature/frontend``
- Resolve any merge conflicts (can do visually)
- Commit changes ``git commit -m "Merging feature/frontend with main"``
- ``git push origin main`` (origin is the configured remote name)


Miscellaneous Commands
``python –m pip freeze > requirements.txt``

### Database Guidelines
The db files (under src) require a mongodb username and password with read and write access to connect to the database. This information was previously shared to you.

When you are ready to run any of the database files, make sure you have created a file named ``.env`` in the main NutriTiger directory. In that file, write the lines:
``MONGODB_USERNAME=<username>``
``MONGODB_PASSWORD=<password>``
Replace ``<username>`` and ``<password>`` with the NutriTiger mongodb username and password accordingly.

Additionally, make sure your current IP address has network access. Go to the MongoDB Atlas Nutritiger project and click on "Network Access" on the left side menu. If you have the message that your current IP address is not added, click to add your current IP address to the access list. You must be connected to password protected WiFi to have network access.

