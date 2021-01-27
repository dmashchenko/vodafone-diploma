import os
from pathlib import Path
import configparser

config = configparser.ConfigParser()
abspath_of_this_script = os.path.abspath(os.path.realpath(__file__))

config.read(os.path.split(abspath_of_this_script)[0] + '/../../../config.cfg')


PROJECT_ROOT = Path(config['DEFAULT']['PROJECT_ROOT'])
RAW_DATA_DIR = Path(config['DEFAULT']['RAW_DATA_DIR'])

PREPROCESSED_DATA_DIR = PROJECT_ROOT / 'ml/data/preprocessed'
