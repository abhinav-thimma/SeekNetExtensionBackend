# SeekNet - Chrome Extension Backend

# Installing dependencies:
> pip install -r src/requirements.txt
> python -m spacy download en_core_web_sm
# connecting a mongo DB instance:
1. Create a new file called 'config.json' in src/ with the following content:
> {\
    "connection_url": "<CONNECTION_URL>",\
     "db_name": "DB_NAME"\
    }

# To run:
> cd src

> flask run
