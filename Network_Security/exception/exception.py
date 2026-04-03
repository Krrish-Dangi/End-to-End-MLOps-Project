import sys
from Network_Security.logging.logger import logging


def my_message(mssg, source:sys):
    _,_,exc_tb = source.exc_info()

    file_name = exc_tb.tb_frame.f_code.co_filename
    line_no = exc_tb.tb_lineno

    return f"\n\n------------Error occured in file {file_name} at line {str(line_no)}, mssg = {mssg}.------------\n\n"

    

class CustomException(Exception):
    def __init__(self, mssg, source:sys):
        super().__init__(mssg,source)
        self.message = my_message(mssg,source)

    def __str__(self):
        return self.message