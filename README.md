# Speech2Text

This is a ongoing development project in which I experiment with transcribing and analysing of spoken language.
I am not entirely sure in which direction I will develop it next, therefore I list here what is currently included 
and what are my ideas to develop further.

Currently, the projects includes following components:
- A main webpage for the interaction with the program which includes
  - Starting, Pausing and stopping a audio recording
  - After stopping the recording a prompt will show up to ask the user if the audio recording shall be transcribed. 
  If the user agrees, the file will be transcribed and both, the raw audio file and the transcription will show up
  in the respective frame in the webpage. 
  - The user can open the raw audio file as well as the transcription by simply clicking on the files. 
  The name of the files include the timestamp of when they were created.
  - A button to delete all audio recordings and transcriptions.
- The recordings and the transcriptions are saved locally in the 'backend/static/output' directory. A link to the 
stored files is contained in a SQLite database. This can be extended to have online storage of the ressources and changing
the stored links to the URLs to the remote data.


Future developments might include but are certainly not limited to:
- having individual users to register  
- allowing a users to have access only to their respective files on the database.
- improving the system visually with a nicer WEB UI e.g. by including some animations, ...
- including a text analysis tool which can analyse the speaking speed, vocabulary, length of pauses, usage of fillers, ...

# Installation
To get the program running, just install the libraries mentioned in the requirements.txt with the python package manager 
by executing one of the following two commands.

```bash
pip install -r requirements.txt
pip3 install -r requirements.txt
```

I recommend to set up a virtual environment for the project and install all the libraries and dependencies there.

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
export FLASK_APP=backend/app.py
export FLASK_ENV=development    # Optional: for debugging
flask run
```


Please be aware that the program was currently tested only on a MacOS system. There might be unexpected behavior
on other operating systems. If you encounter such behavior, please report it to me.

