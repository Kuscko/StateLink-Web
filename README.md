# Django Web Template
This is a Django Web Template meant to provide a springboard for creating a django web application with desired functionalities.

Uses best web development practices for 2024 to my knowledge.

## Features

- Obfuscation of pertenant data for the web application (see settings.py and environment_template.py).
- Customized settings to fit a user-centric web application with a sqlite3 database for the development environment and PostgreSQL database for the production environment.
- User Registration, Login, and Logout views with endpoints.

### Packages Included:
- Django==5.0.6 # Django is a high-level Python web framework that encourages rapid development and clean, pragmatic design.
- psycopg2==2.9.9 # Psycopg is the most popular PostgreSQL database adapter for the Python programming language.
- django-ratelimit=4.1.0 # Django Ratelimit provides a decorator to rate-limit views. 

### Deployment

#### Visual Studio
1. Clone the Repository
2. Open in Visual Studio
3. Change the name of the Folders from `DjangoWebTemplate` to what project name you chose, . i.e. `myproject`.
4. CTRL+SHIFT+F (or MAC equivalent) and search for `DjangoWebTemplate`.
5. Expand the box and type in the repository name you choose and confirm the replacement.
6. Create a Python Virutal Environment <br />
    `CTRL+SHIFT+P` <br />
    `Type: "Environment"` <br />
    `Select: "Create Python Environment."` <br />
    `Select: "venv"` <br />
    `Choose your interpreter.` <br />
      *If you don't see an interpreter available, install python [here](https://www.python.org/downloads/)*
7. Activate your new virtual environment <br />
    Linux: `source ./venv/Scripts/activate`
    Windows: `./venv/Scripts/activate` 
8. Install required packages from requirements.txt <br />
`pip install -r requirements.txt` <br />
9. Run the python migrations to create the database <br />
`python manage.py migrate`
10. Explore the files, especially settings.py and environment_template.py and configure as you see fit.





