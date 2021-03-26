# python3 ~/Drive/workshop/2-current/2-data\ engineering/3_to_df.py


import pathlib
import json

invalid_json_file = pathlib.Path.home() / 'Desktop' / 'almost.json'
valid_json_file = pathlib.Path.home() / 'Desktop' / 'valid.json'


with valid_json_file.open(mode='r') as valid:
    data = json.load(valid)


