from airflow.models import DAG
from airflow.operators.bash import BashOperator

# TODO: what else should I put in the default args for this pipeline?
default_args={"start_date": "2021-01-01"}
git_log_etl = DAG('git_log_etl', default_args=default_args)


repos = [
    # 'https://github.com/spotify/luigi.git',
    # 'https://github.com/apache/airflow.git',
    'https://github.com/scala/scala.git'
]

repo_dirs = [r.split('/')[-1][:-4] for r in repos]

git_log = """git log --pretty=format:']},{%n "commit": "%H",%n "abbreviated_commit": "%h",%n "name": "%aN",%n "email": "%aE",%n "date": "%at",%n"files_changed": [' --numstat --no-merges"""

clone_template="""
cd /root/airflow/repos
rm -rf *
{% for repo in params.repos %}
git clone {{ repo }}
{% endfor %}

{% for dir in params.repo_dirs %}
cd /root/airflow/repos/{{ dir }}
{{ params.git_log }} > /root/airflow/json/{{ dir }}_git_log.json
{% endfor %}

{% for dir in params.repo_dirs %}
cat /root/airflow/json/{{ dir }}_git_log.json | awk -f /root/airflow/dags/process_log.awk > /root/airflow/json/{{ dir }}_awk.json 
{% endfor %}

"""
clone_task = BashOperator(task_id='clone_task',
    bash_command= clone_template,
    params={'repos': repos, 'repo_dirs':repo_dirs, 'git_log':git_log},
    dag=git_log_etl)
