import os
import sys
import logging
from logging.handlers import RotatingFileHandler


logger = logging.getLogger("logs/app_logger")
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

#Консольные логи
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

log_dir = "logs"
log_file = "app.log"
os.makedirs(log_dir, exist_ok=True)

#Файловые логи
file_handler = RotatingFileHandler(os.path.join(log_dir, log_file), maxBytes=10*1024*1024, backupCount=5)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
