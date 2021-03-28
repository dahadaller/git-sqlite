# import json
from pathlib import Path
import sqlite3
import json

from airflow.models import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator

import pandas as pd

def clone_log_awk_args(arg):
    repos = [
        'https://github.com/spotify/luigi.git',
        'https://github.com/scala/scala.git'
    ]

    repo_dirs = [r.split('/')[-1][:-4] for r in repos]

    git_log = """git log --pretty=format:'{"commit": "%H", "abbreviated_commit": "%h", "name": "%aN","email": "%aE","date": "%at", "files_changed": []},' --numstat --no-merges"""

    clone_log_awk_template="""
    # clear out json directory
    cd /root/airflow/data
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
    {{ params.git_log }} > /root/airflow/data/{{ dir }}_git_log.json
    {% endfor %}

    # process git log "json" with awk
    {% for dir in params.repo_dirs %}
    cat /root/airflow/data/{{ dir }}_git_log.json | awk -f /root/airflow/dags/process_log.awk > /root/airflow/data/{{ dir }}_awk.json 
    {% endfor %}

    """

    if arg == 'bash_command':
        return clone_log_awk_template
    if arg == 'params':
        return {'repos': repos, 'repo_dirs':repo_dirs, 'git_log':git_log}

def clean_json_callable():
    data_dir = Path('/root/airflow/data/')
    awk_json_files = list(data_dir.glob('*_awk.json'))
    valid_json_files = [data_dir / (a.stem[:-4] + '_valid' + a.suffix) for a in awk_json_files]


    for ajf, vjf in zip(awk_json_files, valid_json_files):

        with ajf.open(mode='r') as awk_json, vjf.open(mode='w') as valid_json:

            # correct top-level bracket on first line
            valid_json.write('[\n')

            begin, middle, end = '',[],''
            count = 1
            for line in awk_json:

                if line.startswith('{"commit":'):
                    # write out files from previous commit
                    middle = ''.join(middle).rstrip(',')
                    valid_json.write(begin + middle + end)

                    # prepare to populate current commit with files
                    i = line.rfind('[]')
                    begin = line[:i+1]
                    middle = []
                    end = line[i+1:]
                    continue

                if line.startswith('{"lines_added":'):
                    # add file to current commit
                    middle.append(line.rstrip())
                    continue

            # write the last commit to file
            middle = ''.join(middle).rstrip(',')
            end = end.rstrip().rstrip(',') # remove trailing comma for last object in list
            valid_json.write(begin + middle + end)

            # correct top-level bracket on last line
            valid_json.write(']')


def json_df_sqlite_callable():
    data_dir = Path('/root/airflow/data/')
    valid_json_files = data_dir.glob('*_valid.json')

    for valid_json in valid_json_files:

        with valid_json.open(mode='r') as read_json:
            try:
                json_dict = json.load(read_json)
            except ValueError as error: 
                print(str(valid_json))
                raise error

        commits = pd.DataFrame(json_dict)[["commit","abbreviated_commit","name","email","date"]]
        files_changed = pd.json_normalize(json_dict, record_path='files_changed', meta=['commit', 'abbreviated_commit'])

        commits.to_csv(data_dir / (valid_json.stem[:-6] + '_commits.csv'))
        files_changed.to_csv(data_dir / (valid_json.stem[:-6] + '_files_changed.csv'))

        con = sqlite3.connect(data_dir / 'commit.db')
        with con:
            commits.to_sql(valid_json.stem[:-6] + '_commits', con, if_exists="replace")
            files_changed.to_sql(valid_json.stem[:-6] + '_files_changed', con, if_exists="replace")


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

json_df_sqlite = PythonOperator(
    task_id ='json_df_sqlite',
    python_callable=json_df_sqlite_callable,
    dag=git_log_etl)

clone_log_awk >> clean_json >> json_df_sqlite
