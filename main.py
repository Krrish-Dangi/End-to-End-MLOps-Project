from Network_Security.components.data_ingestion import DataIngestion
from Network_Security.components.data_validation import DataValidation
from Network_Security.components.data_transformation import DataTransformation
from Network_Security.components.model_trainer import ModelTrainer
from Network_Security.Exception.exception import NetworkSecurityException
from Network_Security.logging.logger import logging
from Network_Security.entity.config_entity import DataIngestionConfig, DataValidationConfig, DataTransformationConfig, ModelTrainerConfig
from Network_Security.entity.config_entity import TrainingPipelineConfig

import sys

if __name__ == "__main__":
    try:
        training_pipeline_config = TrainingPipelineConfig()

        data_ingestion_config = DataIngestionConfig(
            training_pipeline_config=training_pipeline_config
        )

        data_ingestion = DataIngestion(
            data_ingestion_config=data_ingestion_config
        )

        logging.info("initiate the data ingestion")

        data_ingestion_artifact = data_ingestion.initiate_data_ingestion()
        logging.info("Data ingestion done")
        print(data_ingestion_artifact)

        data_validation_config = DataValidationConfig(training_pipeline_config)
        data_validation = DataValidation(data_ingestion_artifact, data_validation_config)

        logging.info("Initiate the data validation")
        data_validation_artifact = data_validation.initiate_data_validation()
        logging.info("Data Validation done")
        print(data_validation_artifact)
        data_transformation_config=DataTransformationConfig(training_pipeline_config)
        logging.info("data Transformation started")
        data_transformation=DataTransformation(data_validation_artifact,data_transformation_config)
        data_transformation_artifact=data_transformation.initiate_data_transformation()
        print(data_transformation_artifact)
        logging.info("data Transformation completed")
        logging.info("Model Training sstared")
        model_trainer_config=ModelTrainerConfig(training_pipeline_config)
        model_trainer=ModelTrainer(model_trainer_config=model_trainer_config,data_transformation_artifact=data_transformation_artifact)
        model_trainer_artifact=model_trainer.initiate_model_trainer()

        logging.info("Model Training artifact created")


    except Exception as e:
        raise NetworkSecurityException(e, sys)