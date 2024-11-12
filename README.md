# movie-data-uploader

## Introduction

Hi, Apoorv here. I am creating this app to have the following functionalities:

1. APIs for authentication
2. APIs to upload the CSV
3. APIs to track the status of uploaded CSV progress
4. APIs to view uploaded data in the dashboard with pagination and ability to
   sort items based on Date Added, Release Date, Duration.

This app also has a front-end that provides features:

1. Login page
2. Signup page
3. dashboard
4. movie_dashboard with features like view the list of all movies/shows available in the
   system in a paginated view with functionality to sort items based on Date
   Added, Release Date, Duration

> Front-end is not that polished.

> I could have done better if had more time like,
> integrating unittesting, adding celery with redis and more abstraction in code but I guess for now this works.

## Setup and running the system

- first create conda environment after cloning:
  conda create -n data-uploader python=3.12

- activate the environment
  conda activate data-uploader

- cd to the folder where you will find requirements.txt and do the following:
  pip install -r requirements.txt

- Now you need to setup your mongo
  create a db inside your mongo and copy it's uri

- Add mongo uri and db name to conda env:
  conda env config vars set MONGO_URI="your_mongo_uri"
  conda env config vars set DATABASE_NAME="imdb_database"

- Restart conda env:
  conda deactivate
  conda activate data-uploader

- Open 2 terminals, in first cd to backend and in second cd to frontend
  in the backend terminal run command: python run.py
  in the frontend terminal run command: python3 -m http.server 3000

- open the following link in your browser:
  http://127.0.0.1:3000

and you are good to go first do signup then do login.

