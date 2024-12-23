# Speech Analysis

This is an ongoing development project in which I experiment with transcription and analysis of spoken language.
I am not entirely sure in which direction I will develop it next. Therefore, I list here what is currently included 
and what are my ideas to develop further.

Currently, the project includes following components:
- User Management (registration, login, logout, ...)
- Recording, transcribing and analyzing audio recordings
- File Management for audio recording and analysis
- Analysis includes speech rate analysis, pitch analysis, energy analysis, summation of the content and 
suggestion of how to improve the speech. 

Future developments might include but are certainly not limited to:
- making the AI models faster and better and compare their performance
- hosting the whole platform as a website by creating Docker containers, using a PostgreSQL and object storage.

Here is a glimpse into the landing page of the project:
![Alt text](frontend/src/static/figures/entry(1).png)
![Alt text](frontend/src/static/figures/entry(2).png)
![Alt text](frontend/src/static/figures/entry(3).png)

# Installation
To get the program running, install the libraries mentioned in the requirements.txt with the python package manager 
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

Alternatively, you can run the program
from the terminal. To do this, ensure that you are in the root directory and run 

`python src/app.py`

It might happen that python cannot resolve some module paths. To overcome this issue, you can set the `PYTHONPATH` 
environment variable to tell Python where to look for the backend module with 

```bash
export PYTHONPATH=$(pwd)  # on macOS/Linux
set PYTHONPATH=%cd%       # on Windows
```

A third option is to run the program directly via Flask CLI with

```bash
export FLASK_APP=src.app:create_app   # Optional: Set this in the venv/bin/activate
export FLASK_ENV=development          # Optional: User for debugging
flask run
```

Setting the path to the `FLASK_APP` might also be necessary when running the program from the IDE or terminal.
Please be aware that the program was currently tested only on a MacOS system. There might be unexpected behavior
on other operating systems. If you encounter such behavior, please report it to me.


