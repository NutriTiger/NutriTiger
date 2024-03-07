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