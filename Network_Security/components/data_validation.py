from Network_Security.entity.artifact_entity import DataIngestionArtifact, DataValidationArtifact
from Network_Security.entity.config_entity import DataValidationConfig
from Network_Security.Exception.exception import NetworkSecurityException
from Network_Security.logging.logger import logging
from Network_Security.constants.training_pipeline import SCHEMA_FILE_PATH
from Network_Security.utils.main_utils.utils import read_yaml_file, write_yaml_file
from scipy.stats import ks_2samp # For the data drift calc
import pandas as pd
import os, sys

class DataValidation:
    def __init__(self, data_ingestion_artifact: DataIngestionArtifact,
                 data_validation_config: DataValidationConfig):
        try:
            self.data_ingestion_artifact = data_ingestion_artifact
            self.data_validation_config = data_validation_config
            self._schema_config = read_yaml_file(SCHEMA_FILE_PATH)
        except Exception as e:
            raise NetworkSecurityException(e, sys)
        
    @staticmethod
    def read_data(file_path) -> pd.DataFrame:
        try:
            return pd.read_csv(file_path)
        except Exception as e:
            raise NetworkSecurityException(e, sys)
        
    def validate_number_of_colums(self, dataframe:pd.DataFrame) -> bool:
        try:
            number_of_columns = len(self._schema_config["columns"])
            logging.info(f"Required number of columns: {number_of_columns}")
            logging.info(f"Data frame has columns: {len(dataframe.columns)}")
            if len(dataframe.columns) == number_of_columns:
                return True
            return False
        except Exception as e:
            raise NetworkSecurityException(e, sys)
        
    def validate_numerical_columns(self, dataframe:pd.DataFrame) -> list:
        try:
            expected_numerical_col = self._schema_config["numerical_columns"]
            actual_col = dataframe.columns

            missing_col = []

            for i in expected_numerical_col:
                if i not in actual_col:
                    missing_col.append(i)

            return actual_col
        except Exception as e:
            raise NetworkSecurityException(e, sys)
        
    def detect_dataset_drift(self, base_df:pd.DataFrame, current_df:pd.DataFrame, threshold=0.05)->bool:
        try:
            status = True
            report = {}
            for column in base_df.columns:
                d1 = base_df[column]
                d2 = current_df[column]
                is_same_dist = ks_2samp(d1, d2)
                if threshold <= is_same_dist.pvalue:
                    is_found = False
                else:
                    is_found = True
                    status = False

                report.update(
                    {
                        column:{
                        "p_value" : float(is_same_dist.pvalue),
                        "drift_status" : is_found
                                }
                    }
                )

            drift_report_file_path = self.data_validation_config.drift_report_file_path
            write_yaml_file(drift_report_file_path, report)

            return status

        except Exception as e:
            raise NetworkSecurityException(e, sys)
        
    def initiate_data_validation(self) -> DataValidationArtifact:
        try:
            train_file_path = self.data_ingestion_artifact.trained_file_path
            test_file_path = self.data_ingestion_artifact.test_file_path

            train_dataframe = DataValidation.read_data(train_file_path)
            test_dataframe = DataValidation.read_data(test_file_path)


            status = self.validate_number_of_colums(dataframe=train_dataframe)
            error_message = ""
            if not status:
                error_message = "Train Dataframe does not contain all columns.\n"

            status = self.validate_number_of_colums(dataframe=test_dataframe)
            if not status:
                error_message = "Test Dataframe does not contain all columns.\n"

            missing_cols = self.validate_numerical_columns(dataframe=train_dataframe)
            if len(missing_cols) != 0:
                error_message = f"Train Dataframe does not have all the numerical columns. Missing ones = {missing_cols}"
            
            missing_cols = self.validate_numerical_columns(dataframe=test_dataframe)
            if len(missing_cols) != 0:
                error_message = f"Test Dataframe does not have all the numerical columns. Missing ones = {missing_cols}"
            
            status = self.detect_dataset_drift(train_dataframe, test_dataframe)
            dir_path = os.path.dirname(self.data_validation_config.valid_train_file_path)
            os.makedirs(dir_path, exist_ok=True)
            
            train_dataframe.to_csv(
                self.data_validation_config.valid_train_file_path, index=False, header=True
            )

            test_dataframe.to_csv(
                self.data_validation_config.valid_test_file_path, index=False, header=True
            )

            data_validation_artifact = DataValidationArtifact(
                validation_status=status,
                valid_train_file_path=self.data_ingestion_artifact.trained_file_path,
                valid_test_file_path=self.data_ingestion_artifact.test_file_path,
                invalid_train_file_path=None,
                invalid_test_file_path=None,
                drift_report_file_path=self.data_validation_config.drift_report_file_path,
            )
            return data_validation_artifact
        except Exception as e:
            raise NetworkSecurityException(e, sys)