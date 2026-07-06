1. run 
  python -m venv testapps
at project root

2. activate venv(activate.bat in "venvname"/Scripts),
   then
    pip install requirements.txt

4. cd front 
  then run "python -m uvicorn app:app --reload"

5. run apps
  python client.py(cli app)
