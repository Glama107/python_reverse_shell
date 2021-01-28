# Python-Reverse-Shell

This is a **fully working reverse shell** get from Youtube tutorial and edited by me to add more functionnality.
It comes with a server.py and client.py. The reverse shell is based on the connection from the client to the server.
There is a Received folder inside, it's required for the screenshot and downloading function.


## Installation
To install this project, I'm based on a DigitalOcean Ubuntu server.
Before starting, just make an `sudo apt-get update` 

For starting, clone the project  on your machine :

    $ git clone https://github.com/glama107/python_reverse_shell.git 
    $ cd python_reverse_shell/
Then, you have to use Python 3.9 or +, to see and upgrade Python, see the Upgrade Python part.

You have to install pip3 command:

    $ sudo apt install python3-pip		
Then you have to install the dependency:

    $ pip3 install tqdm
    $ pip3 install pyscreenshot
    $ pip3 install pillow
And now you can run the server with `python3 server.py`, for the client, it's python3 client.py :

## Compilation of the client

To compile in one file executable , we use `pyinstaller`, it's the simple and best way for our project.
to get a `.exe` you have to do it on a Windows client, for Linux it's a binary file.
So, let's start:

    $ pip3 install pyinstaller
    $ sudo apt-get install libpython3.9-dev
Here, **3.9** is my version of Python, you just have to put our version of Python.

Then you just have to build the compiled file :

    $ pyinstaller --onefile --noconsole client.py
The `--onefile` is to get only one file compiled with all packages includes, and the `--noconsole` is for running the app in background so nobody can see the app running ( it's only appear in the Task Manager ).
The build is in `dist/` folder 

## Upgrade python

If you have python 3.x.x and you want to upgrade your version for linux, you have to follow step by step this guide :
First, display your current version of python with `python3 -V`

    $ python3 -V 
    Python 3.8.5
Then, you have to download the lastest version of Python, for me it's `3.9.0`

    $ sudo apt-get install python3.9
Change the python update alternative :

    $ sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.8 1
    update-alternatives: using /usr/bin/python3.8 to provide /usr/bin/python3 (python3) in auto mode
    
    $ sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.9 2
    update-alternatives: using /usr/bin/python3.9 to provide /usr/bin/python3 (python3) in auto mode

And finally, change the default updated version of python 
```
    $ sudo update-alternatives --config python3
There are 2 choices for the alternative python3 (providing /usr/bin/python3).

  Selection    Path                Priority   Status
------------------------------------------------------------
* 0            /usr/bin/python3.9   2         auto mode
  1            /usr/bin/python3.8   1         manual mode
  2            /usr/bin/python3.9   2         manual mode

Press <enter> to keep the current choice[*], or type selection number: 0
```
Now if you make `python3 -V` you get the lastest downloaded version of Python.
