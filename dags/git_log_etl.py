# import json
from pathlib import Path
import sqlite3

from airflow.models import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator

import pandas as pd

def clone_log_awk_args(arg):
    repos = [
        # 'https://github.com/spotify/luigi.git',
        # 'https://github.com/apache/airflow.git',
        'https://github.com/scala/scala.git'
    ]

    repo_dirs = [r.split('/')[-1][:-4] for r in repos]

    git_log = """git log --pretty=format:']},{%n "commit": "%H",%n "abbreviated_commit": "%h",%n "name": "%aN",%n "email": "%aE",%n "date": "%at",%n"files_changed": [' --numstat --no-merges"""

    clone_log_awk_template="""
    # clear out json directory
    cd /root/airflow/json
    rm -rf *.json
    rm -rf *.csv
    rm -rf *.db

    # clear out repos
    cd /root/airflow/repos
    rm -rf *

    # clone each repo
    {% for repo in params.repos %}
    git clone {{ repo }}
    {% endfor %}

    # pipe prettified "json" git log to file
    {% for dir in params.repo_dirs %}
    cd /root/airflow/repos/{{ dir }}
    {{ params.git_log }} > /root/airflow/json/{{ dir }}_git_log.json
    {% endfor %}

    # process git log "json" with awk
    {% for dir in params.repo_dirs %}
    cat /root/airflow/json/{{ dir }}_git_log.json | awk -f /root/airflow/dags/process_log.awk > /root/airflow/json/{{ dir }}_awk.json 
    {% endfor %}

    """

    if arg == 'bash_command':
        return clone_log_awk_template
    if arg == 'params':
        return {'repos': repos, 'repo_dirs':repo_dirs, 'git_log':git_log}

def clean_json_callable():
    json_dir = Path('/root/airflow/json/')
    awk_json_files = list(json_dir.glob('*_awk.json'))
    valid_json_files = [json_dir / (a.stem[:-4] + '_valid' + a.suffix) for a in awk_json_files]

    print(list(awk_json_files),valid_json_files)
    print(list(zip(awk_json_files, valid_json_files)))

    # find line indices of awk_json that should be 
    # edited before writing to valid. These just 
    # looking for lines between square brackets [] using a stack to remove the 
    # comma of the last element in each list.
    # also want to remove the comma from the last line
    for ajf in awk_json_files:

        with ajf.open(mode='r') as awk_json:

            comma_lines = set()
            last_line_number = 0

            stack = []
            between_brackets = False
            
            for line_number, line in enumerate(awk_json):

                last_line_number = line_number

                if line_number == 0:
                    pass

                elif line.rfind('[')!=-1:
                    between_brackets = True

                elif line.find(']')!=-1:
                    between_brackets = False

                    if stack:
                        line_num, line_text = stack.pop()
                        while stack and line_text.rfind(',') == -1:
                            line_num, line_text = stack.pop()

                        comma_lines.add(line_num)
                        stack = []
                
                elif between_brackets:
                    stack.append((line_number, line))
                    
            comma_lines.add(last_line_number)


    for ajf, vjf in zip(awk_json_files, valid_json_files):
        # edit and write lines to valid
        with ajf.open(mode='r') as awk_json, vjf.open(mode='w') as valid_json:

            # correct top-level bracket on first line
            # and add { for furst element
            valid_json.write('[{\n')
    
            for line_number, line in enumerate(awk_json):

                if line_number == 0:
                    continue

                elif line_number in comma_lines:
                    comma_index = line.rfind(',')
                    valid_json.write(line[:comma_index])
                    comma_lines.remove(line_number)
                else:
                    valid_json.write(line)
        
            # correct top-level bracket on last line
            valid_json.write(']}]')

        # # check that json loads and raise an error if it doesn't
        # with vjf.open(mode='r') as valid_json:
        #     data = json.load(valid_json)

def json_df_csv_callable():
    json_dir = Path('/root/airflow/json/')
    valid_json_files = json_dir.glob('*_valid.json')

    for valid_json in valid_json_files:
        df = pd.read_json(valid_json)
        df.to_csv(json_dir / (valid_json.stem + '.csv'))

        # con = sqlite3.connect(json_dir / 'commit.db')
        # with con:
        #     df.to_sql(valid_json.stem[:-6], con, if_exists="replace")


# TODO: what else should I put in the default args for this pipeline?
default_args={"start_date": "2021-01-01"}
git_log_etl = DAG('git_log_etl', default_args=default_args)

clone_log_awk = BashOperator(task_id='clone_log_awk',
    bash_command= clone_log_awk_args('bash_command'),
    params=clone_log_awk_args('params'),
    dag=git_log_etl)

clean_json = PythonOperator(
    task_id='clean_json',
    python_callable=clean_json_callable,
    dag=git_log_etl)

json_df_csv = PythonOperator(
    task_id ='json_df_csv',
    python_callable=json_df_csv_callable,
    dag=git_log_etl)

clone_log_awk >> clean_json >> json_df_csv
