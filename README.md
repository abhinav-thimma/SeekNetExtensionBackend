# SeekNet - Chrome Extension Backend

This repository is the backend flask application for the SeekNet Chrome extension: (https://github.com/abhinav-thimma/SeekNetChromeExtension)
# Installing dependencies:
### Installing packages
> pip install -r src/requirements.txt
### Downloading Spacy english dictionary
> python -m spacy download en_core_web_sm

# Creating a MongoDB Database and Collections:
1. Create a new MongoDB database with a name "seeknet" ( Can be hosted or local )
2. In the database, create 2 collections with the names "extension_actions" and "extension_collections"
3. Make a note of connection URL for your MongoDB instance
# Connecting a mongo DB instance:
1. Create a new file called 'config.json' in src/ with the following content:
```
    {
      "connection_url": "<CONNECTION_URL>",
      "db_name": "<DB_NAME>"
    }
```
2. Replace <CONNECTION_URL> with the connection URL for your mongo DB instance
3. Replace DB_NAME with "seeknet"

# To run the backend:
```
> cd src
> flask run
```
