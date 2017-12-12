Install python 3.5 or greater on your computer
Make a virtual environment by cd'ing to a suitable folder and do python -m venv myenv
Run Scripts\activate.bat in the folder to launch your virtual environment

Go to the project folder and do pip install -r requirements.txt.

Try run the script by "python access-stuff.py". There may be some packages I left out of the requirements.txt, in which case you'll have to install them on your own. Do pip install x, or python easy_install x. 

The main file really is the access-stuff.py, which draws on some functions in functions.py and extracts info from the accessions. Then there's the plantings.py which is thankfully a lot simpler, which just extracts plantings. 

The script currently outputs a csv which then gets converted to dbf by a separate python 2 script. But if I were whoever is reading this I would change this script so it outputs a dbf directly using https://pypi.python.org/pypi/dbf/

Also the file paths in the script probably all need fixing.