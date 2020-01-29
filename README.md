# AI Interview Tool

Flask Web Project, using Flask-SQLAlchemy SQLite database, Bulma CSS Framework

## Instructions to Setup :

* Clone this repository.
* Use `git clone https://github.com/yaiestura/ai_interview.git` to clone this repository  to your computer
* Install pip3 on your system by `sudo apt-get install python3-pip` if not already installed.
* Create a virtual environment by the name of **venv**. Information in setting up virtualenv can be found [here](https://docs.python-guide.org/dev/virtualenvs/ "Pipenv & Virtual Environments").
* Activate your virtualenv by `source venv/bin/activate` script
* Execute a `pip3 install -r requirements.txt` command to install the required packages.

## Working :

* Open a terminal and enter `python3 run.py`
* Also you need to run redis by celery command`celery app.celery worker --loglevel=info`
* Finally, go to `localhost:5000` to display the start page of application.
