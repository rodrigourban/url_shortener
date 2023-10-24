# URL shortener.

### Welcome to my url shortner API created with FASTApi.

To run the project you first need to create a virtual environment
```
python3 -m venv venv
source venv/bin/activate (mac)
venv\Scripts\activate.bat (Windows)
```

Install the required packages
```
pip install -r requirements.txt
```

Run project with
```
uvicorn src.main:app --reload
```

You can see full documentation of the endpoints and test the app in:
```
localhost:8000/docs
```

To run tests
```
pytest
```

If you have any doubts please reach out to me. <br>
<i>Rodrigo</i>