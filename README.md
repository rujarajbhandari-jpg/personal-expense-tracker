********************************
Group Project: Personal-Expense-Tracker

Please follow these simple steps to set it up:

*********************************

1. Download & Extract the Folder

Save the attached ZIP file

Right-click → Extract All (Windows)
or double-click to unzip (Mac)

You should see the project folder:

personal-expense-tracker/

*********************************
2. Make sure Python 3 is installed

Open a terminal / command prompt and run:

python3 --version
If you see a version like 3.x.x, you’re all set.

*********************************

3. Create and Activate Virtual Environment

Inside the extracted project folder, run:

Mac/Linux:

python3 -m venv venv
source venv/bin/activate

Windows (PowerShell):

python -m venv venv
venv\Scripts\activate

You should now see (venv) in the terminal prompt.

*********************************

 4. Install Required Libraries

Run:

pip install flask
That’s all you need — the project uses SQLite, which is built into Python.

*********************************

5. Initialize the Database

Run the initialization script:

python3 init_db.py
You should see:

Database initialized successfully.

************************
 6. Run the Application

Start the web server:

python3 run.py
Open your browser and go to:

http://127.0.0.1:5000
You can now register, log in, add expenses, and view history.

************************
