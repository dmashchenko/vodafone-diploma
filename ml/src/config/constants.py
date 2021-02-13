import os
from pathlib import Path
import configparser

config = configparser.ConfigParser()
abspath_of_this_script = os.path.abspath(os.path.realpath(__file__))

PROJECT_ROOT = Path(os.path.split(abspath_of_this_script)[0] + '/../../..').resolve()

config.read(PROJECT_ROOT / 'config.cfg')

RAW_DATA_DIR = Path(config['DEFAULT']['RAW_DATA_DIR'])

PREPROCESSED_DATA_DIR = PROJECT_ROOT / 'ml/data/preprocessed'

RESULT_DIR = PROJECT_ROOT / 'result'
