from Network_Security.Exception.exception import NetworkSecurityException
from Network_Security.logging.logger import logging


from Network_Security.entity.config_entity import DataIngestionConfig
from Network_Security.entity.artifact_entity import DataIngestionArtifact

import os
import sys
import numpy as np
import pandas as pd
import pymongo
from sklearn.model_selection import train_test_split

import dotenv
dotenv.load_dotenv()

uri = os.getenv("MONGO_DB_URL")


class DataIngestion:
    def __init__(self, data_ingestion_config: DataIngestionConfig):
        try:
            self.data_ingestion_config = data_ingestion_config
        except Exception as e:
            raise NetworkSecurityException(e, sys)
        
    def export_mongo_data_to_dataframe(self):
        collection_name = self.data_ingestion_config.collection_name
        database_name = self.data_ingestion_config.database_name

        self.mongo_client = pymongo.MongoClient(uri)

        collection = self.mongo_client[database_name][collection_name]

        df = pd.DataFrame(list(collection.find()))
        if "_id" in df.columns.to_list():
            df=df.drop(columns=["_id"],axis=1)

        df.replace({"na":np.nan},inplace=True)
        return df
    
    def export_data_to_feature_store(self, df: pd.DataFrame):
        try:
            feature_store_file_path = self.data_ingestion_config.feature_store_file_path
            dir_path = os.path.dirname(feature_store_file_path)
            os.makedirs(dir_path, exist_ok=True)
            df.to_csv(feature_store_file_path, index=False, header=True)
            return df
        except Exception as e:
            raise NetworkSecurityException(e, sys)
        
    def train_test_split_data(self, df: pd.DataFrame):
        try:
            logging.info("initiating train test split on the dataframe")
            train_set, test_set = train_test_split(df, test_size=self.data_ingestion_config.train_test_split_ratio)
            logging.info("Performed train test split on the dataframe")

            logging.info("Saving the train and test data")
            dir_path = os.path.dirname(self.data_ingestion_config.training_file_path)
            os.makedirs(dir_path, exist_ok=True)

            train_set.to_csv(self.data_ingestion_config.training_file_path, index=False, header=True)
            test_set.to_csv(self.data_ingestion_config.testing_file_path, index=False, header=True)
            logging.info("Saved train and test data")

        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def initiate_data_ingestion(self):
        try:
            dataframe = self.export_mongo_data_to_dataframe()
            dataframe = self.export_data_to_feature_store(dataframe)
            self.train_test_split_data(dataframe)
            self.data_ingestion_artifact = DataIngestionArtifact(
                trained_file_path= self.data_ingestion_config.training_file_path,
                test_file_path= self.data_ingestion_config.testing_file_path
            )

            return self.data_ingestion_artifact
        except Exception as e:
            raise NetworkSecurityException(e, sys)


