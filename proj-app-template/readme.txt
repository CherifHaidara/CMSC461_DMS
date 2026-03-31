
your_project_folder/
│
├── app.py                 # main entry point
├── utils.py               # shared database and decorator tools
│
├── blueprints/            # router (functionality) files
│   ├── auth.py
│   └── instructors.py
│
└── templates/             # HTML files (Jinja2 templates)
    ├── layout.html
    ├── login.html
    ├── register.html
    └── ...

Notes:
- Python must be in the path
- Easiest environment is installing miniconda
    - it comes with latest python
- installation of flask and mysql-connector is required
    >> pip install Flask mysql-connector-python
- run the server (app.py)
- access the webpages in browser using:
    - http://127.0.0.1:8000/
    - http://localhost:8000/
- login assumes there is a users table in the database
    - CREATE TABLE IF NOT EXISTS users (
        id INT AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(255) UNIQUE,
        password VARCHAR(255)
      );
- the database information is in utils.py
    - the info can be modified accordingly