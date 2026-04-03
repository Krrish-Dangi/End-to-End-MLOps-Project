import os
import logging
from datetime import datetime


date_and_time = datetime.now().strftime("%d_%m_%Y -- %H_%M_%S")
log_file = f"{date_and_time}.log"

folder_path = os.path.join(os.getcwd(), "logs")

os.makedirs(folder_path, exist_ok=True)

file_path = os.path.join(folder_path, log_file)

logging.basicConfig(
    filename= file_path,
    format= "[ %(asctime)s ] %(lineno)d %(name)s - %(levelname)s - %(message)s",
    level= logging.INFO,
)

logging.info("Hello")