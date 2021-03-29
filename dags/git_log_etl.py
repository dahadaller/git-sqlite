from pathlib import Path
import sqlite3
import json

from airflow.models import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from airflow.models import Variable

import pandas as pd

Variable.set("data_dir", "/root/airflow/data")
Variable.set("repos_dir", "/root/airflow/repos")
Variable.set(
    "repo_urls",
    "https://github.com/spotify/luigi.git,https://github.com/scala/scala.git",
)


def clean_awk_output_callable():
    data_dir = Path(Variable.get("data_dir"))
    awk_json_files = list(data_dir.glob("*_awk.json"))
    valid_json_files = [
        data_dir / (a.stem[:-4] + "_valid" + a.suffix) for a in awk_json_files
    ]

    for ajf, vjf in zip(awk_json_files, valid_json_files):

        with ajf.open(mode="r") as awk_json, vjf.open(mode="w") as valid_json:

            # correct top-level bracket on first line
            valid_json.write("[\n")

            begin, middle, end = "", [], ""
            count = 1
            for line in awk_json:

                if line.startswith('{"commit":'):
                    # write out files from previous commit
                    middle = "".join(middle).rstrip(",")
                    valid_json.write(begin + middle + end)

                    # prepare to populate current commit with files
                    i = line.rfind("[]")
                    begin = line[: i + 1]
                    middle = []
                    end = line[i + 1 :]
                    continue

                if line.startswith('{"lines_added":'):
                    # add file to current commit
                    middle.append(line.rstrip())
                    continue

            # write the last commit to file
            middle = "".join(middle).rstrip(",")
            end = end.rstrip().rstrip(
                ","
            )  # remove trailing comma for last object in list
            valid_json.write(begin + middle + end)

            # correct top-level bracket on last line
            valid_json.write("]")


def export_to_sqlite_callable():
    data_dir = Path(Variable.get("data_dir"))
    valid_json_files = data_dir.glob("*_valid.json")

    for valid_json in valid_json_files:

        with valid_json.open(mode="r") as read_json:
            try:
                json_dict = json.load(read_json)
            except ValueError as error:
                print(str(valid_json))
                raise error

        commits = pd.DataFrame(json_dict)[
            ["commit", "abbreviated_commit", "name", "email", "date"]
        ]
        files_changed = pd.json_normalize(
            json_dict,
            record_path="files_changed",
            meta=["commit", "abbreviated_commit"],
        )

        commits.to_csv(data_dir / (valid_json.stem[:-6] + "_commits.csv"))
        files_changed.to_csv(data_dir / (valid_json.stem[:-6] + "_files_changed.csv"))

        con = sqlite3.connect(data_dir / "commit.db")
        with con:
            commits.to_sql(valid_json.stem[:-6] + "_commits", con, if_exists="replace")
            files_changed.to_sql(
                valid_json.stem[:-6] + "_files_changed", con, if_exists="replace"
            )


git_log_etl = DAG("git_log_etl", default_args={"start_date": "2021-01-01"})

clear_data_dir = BashOperator(
    task_id="clear_data_dir",
    bash_command="""
    cd {{ var.value.data_dir }}
    rm -rf *.json
    rm -rf *.csv
    rm -rf *.db
    """,
    dag=git_log_etl,
)

clear_repos_dir = BashOperator(
    task_id="clear_repos_dir",
    bash_command="""
    cd {{ var.value.repos_dir }}
    rm -rf *
    """,
    dag=git_log_etl,
)

git_clone = BashOperator(
    task_id="git_clone",
    bash_command="""
    cd {{ var.value.repos_dir }}
    {% for repo in params.repos %}
    git clone --no-checkout {{ repo }}
    {% endfor %}
    """,
    params={"repos": Variable.get("repo_urls").split(",")},
    dag=git_log_etl,
)

git_log = BashOperator(
    task_id="git_log",
    bash_command="""
    {% for repo_name in params.repo_names %}
    cd {{ var.value.repos_dir }}/{{ repo_name }}
    {{ params.git_log }} > {{ var.value.data_dir }}/{{ repo_name }}_git_log.json
    {% endfor %}
    """,
    params={
        "repo_names": [
            r.split("/")[-1][:-4] for r in Variable.get("repo_urls").split(",")
        ],
        "git_log": """git log --pretty=format:'{"commit": "%H", "abbreviated_commit": "%h", "name": "%aN","email": "%aE","date": "%at", "files_changed": []},' --numstat --no-merges""",
    },
    dag=git_log_etl,
)

awk = BashOperator(
    task_id="awk",
    bash_command="""
    {% for repo_name in params.repo_names %}
    cat {{ var.value.data_dir }}/{{ repo_name }}_git_log.json | awk -f /root/airflow/dags/process_log.awk > {{ var.value.data_dir }}/{{ repo_name }}_awk.json 
    {% endfor %}
    """,
    params={
        "repo_names": [
            r.split("/")[-1][:-4] for r in Variable.get("repo_urls").split(",")
        ]
    },
    dag=git_log_etl,
)

clean_awk_output = PythonOperator(
    task_id="clean_awk_output",
    python_callable=clean_awk_output_callable,
    dag=git_log_etl,
)

export_to_sqlite = PythonOperator(
    task_id="export_to_sqlite",
    python_callable=export_to_sqlite_callable,
    dag=git_log_etl,
)

clear_data_dir >> clear_repos_dir >> git_clone >> git_log >> awk >> clean_awk_output >> export_to_sqlite
