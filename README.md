# Speech2Text

This is a ongoing development project in which I experiment with transcription and analysis of spoken language.
I am not entirely sure in which direction I will develop it next, therefore I list here what is currently included 
and what are my ideas to develop further.

Currently, the projects includes following components:
- Registration of new users and log in for already registered users
- A main webpage for the interaction with the program which includes the recording of audio files and transcribing them.
- Possibility to listen to recorded audios and read the transcriptions in a new tab in the browser. 
The name of the files include the timestamp of when they were created.
- Possibility to delete all audio files for the currently logged-in user. 
At the moment it is not possible to delete single files.
- All files are stored with respect to the currently logged-in user. This is tracked via a SQLite database in the backend.
- The recordings and the transcriptions are saved locally in the 'backend/static/output' directory. A link to the 
stored files is contained in a SQLite database.

Future developments might include but are certainly not limited to:
- extending the interaction with the files, e.g. deleting single files, changing their name, ...
- including a text analysis tool which can analyse the speaking speed, vocabulary, length of pauses, usage of fillers, ...
- hosting the whole platform as a website by switching to PostgreSQL and storing the user files on a cloud

# Installation
To get the program running, just install the libraries mentioned in the requirements.txt with the python package manager 
by executing one of the following two commands.

```bash
pip install -r requirements.txt
pip3 install -r requirements.txt
```

I recommend setting up a virtual environment for the project and install all the libraries and dependencies there.
Use python@3.11 to set up the program, otherwise the Whisper package from OpenAI may fail as it currently only supports
Python 3.8 to 3.11.

# Usage
You can run the program directly in your preferred IDE from the app.py file. 

Alternatively you can run the program
from the terminal. To do this, ensure that you are in the root directory and run 

`python backend/app.py`

It might happen that python cannot resolve some module paths. To overcome this issue, can set the `PYTHONPATH 
environment variable to tell Python where to look for the backend module with 

```bash
export PYTHONPATH=$(pwd)  # on macOS/Linux
set PYTHONPATH=%cd%       # on Windows
```


A third option is to run the program directly via Flask CLI with

```bash
export FLASK_APP=src/app.py
export FLASK_ENV=development    # Optional: for debugging
flask run
```


Please be aware that the program was currently tested only on a MacOS system. There might be unexpected behavior
on other operating systems. If you encounter such behavior, please report it to me.


