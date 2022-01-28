import pandas as pd
import boto3
import logging
import os
from io import StringIO

LOG = logging.getLogger()
LOG.setLevel(logging.INFO)
logHandler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logHandler.setFormatter(formatter)
LOG.addHandler(logHandler)

def handler(event, context):
    try:
        s3 = boto3.client('s3', aws_access_key_id=os.environ.get('ACCESS_ID'),
         aws_secret_access_key=os.environ.get('ACCESS_KEY'))
        LOG.info("s3 created")
        # 's3' is a key word. create connection to S3 using default config and all buckets within S3
        bucket = 'cdk-hnb659fds-assets-467432152884-us-east-1'
        file = "movies.csv"
        obj = s3.get_object(Bucket= bucket, Key= file) 
        # get object and file (key) from bucket
        
        movies = pd.read_csv(obj['Body'])
        LOG.info("data read")
        
        LOG.info("start data cleaning")
        movies_clean = clean_data(movies)
        
        LOG.info("write clean data to s3")
        
        csv_buffer = StringIO()
        movies_clean.to_csv(csv_buffer)
        s3.Object(bucket, 'movies_clean.csv').put(Body=csv_buffer.getvalue())
        
        return {'statusCode': 200, "body": {"message": "Success Cleaning Data"}}
    except Exception as e:
        LOG.error("error while handling lambda event")
        return {'statusCode': 500, "body": {"message": "Failed", 'what': e}}
    

def clean_data(df):
    # remove weird looking index
    movies_copy = df.drop(
        [
            " Rose Namajunas vs. Zhang Weili (Strawweight)",
            " Frankie Edgar vs. Marlon Vera (Bantamweight)",
            " Shane Burgos vs. Billy Quarantillo (Featherweight)",
            " Justin Gaethje vs. Michael Chandler (Lightweight)",
            " - Just Desserts",
            " - If The Hue Fits",
            " - Dust Up",
            " - Scents And Sensibility",
            " - Just One Of The Girls",
            " - Volleybug",
            " - Hide And Tink",
            " - Rainbow's Ends",
            " - Fawn And Games",
            " - Magic Tricks",
        ]
    )
    
    LOG.info("change datatypes")
    # # change datatypes
    movies_copy["id"] = movies_copy["id"].astype("int")
    movies_copy["release_date"] = pd.to_datetime(movies_copy["release_date"])
    
    # drop duplicates
    LOG.info("drop duplicates")
    movies_copy = movies_copy.drop_duplicates()
    
    # select columns we want
    LOG.info("select columns we want")
    movies_copy = movies_copy.drop(["tagline", "overview"], axis=1)
    
    # handle missing values

    LOG.info("drop rows with missing values")
    # select columns we want
    movies_copy = movies_copy.dropna(axis=0, how="all")
    
    # replace nan in revenue and runtime with mean
    LOG.info("replace nan in revenue and runtime with mean")
    movies_copy.revenue.fillna(movies_copy.revenue.mean(), inplace=True)
    movies_copy.runtime.fillna(movies_copy.runtime.mean(), inplace=True)
    
    # drop all release date unknown
    LOG.info("drop all release date unknown")
    movies_copy.dropna(inplace=True)
    
    return movies_copy
    