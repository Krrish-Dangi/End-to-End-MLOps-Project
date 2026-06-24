import os
import sys
import json
import pymongo

import certifi ## certifi provides a bundle of trusted SSL/TLS certificates (CA certificates) that Python programs can use to verify that they're connecting to legitimate HTTPS servers.
import pandas as pd
import numpy as np
from Network_Security.Exception.exception import NetworkSecurityException
from Network_Security.logging.logger import logging

from dotenv import load_dotenv
load_dotenv()

uri = os.getenv("MONGO_DB_URL")

ca = certifi.where() ## all the CAs

class NetworkDataExtraction():
    def __init__(self):
        try:
            pass
        except Exception as e:
            raise NetworkSecurityException(e, sys)
        
    def csv_to_json(self, file_path):
        try:
            df = pd.read_csv("Network_Data\phisingData.csv") ## Extract
            df.reset_index(drop=True, inplace=True)
            records = list(json.loads(df.T.to_json()).values()) ## Transform
            ## records = df.to_dict(orient="records") // Easy and fast alternative
            return records
            
        except Exception as e:
            raise NetworkSecurityException(e, sys)
        
    def insert_data_mongoDB(self, records, database, collection): ## Load
        try:
            self.database=database
            self.collection=collection
            self.records=records

            self.mongo_client=pymongo.MongoClient(uri)
            self.database = self.mongo_client[self.database]
            
            self.collection=self.database[self.collection]
            self.collection.insert_many(self.records)
            return(len(self.records))
        
        except Exception as e:
            raise NetworkSecurityException(e, sys)
        

if __name__=='__main__':
    FILE_PATH="Network_Data\phisingData.csv"
    DATABASE="Network_Security_DB"
    Collection="NetworkData"
    networkobj=NetworkDataExtraction()
    records=networkobj.csv_to_json(file_path=FILE_PATH)
    print(records)
    no_of_records=networkobj.insert_data_mongoDB(records,DATABASE,Collection)
    print(no_of_records)