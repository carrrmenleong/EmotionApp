# EmotionApp

Emotion app is a web application that can record learners’ emotions in real time and allow researchers to customize questionnaires.

## Getting Started for development

### 1. Clone the repository

```
$ git clone https://github.com/carrrmenleong/EmotionApp.git
$ cd EmotionApp
```

### 2. Create and activate a virtual environment

Unix/Linux:

```
$ python -m venv venv
$ source venv/bin/activate
```

Windows:

```
$ python -m venv venv
$ venv\Scripts\activate
```

### 3. Install requirements

```
$ pip install -r requirements.txt
```

### 4. Setup database

```
$ flask db upgrade
```

### 5. Setup database for testing (optional)

Copy app.db file and rename the copied file to test.db which will be used during testing


### 6. Run the application

```
$ flask run
```

## Development Workflow

1. Choose the issue you want to work on.
2. Assign yourselves to the relevant issue on GitHub.
3. Create a branch corresponding to the issue with the format `i<issue_number>-<issue_name>`.
4. Checkout to the issue branch.
5. Work on your changes.
6. Make commits and push them to the issue branch.
7. Open a pull request on GitHub.
8. Get your peer to review your code and merge your change to main.
9. Your feature is merged.
10. Delete your local branch with `git branch -d <branch_name>`.

## Development Practise
### 1. Update requirements.txt
After installing new pakage(s), run the following code in your virtual environment to update the requirements.txt file. 
```
$ pip freeze > requirements.txt
```
To download the pakages listed in the requirements.txt file, run the following code in your virtual environment.
```
$ pip install -r requirements.txt
```

## Testing the application (backend)
### 1. Run the unit and funcional tests
```
$ python -m pytest -v --disable-warnings --cov=app --cov-report html 
```
### 2. Read the test report
Open up htmlcov/index.html to read the test report
