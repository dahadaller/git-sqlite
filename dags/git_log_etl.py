from airflow.models import DAG
from airflow.operators.bash_operator import BashOperator

# TODO: what else should I put in the default args for this pipeline?
default_args={"start_date": "2021-01-01"}
git_log_etl = DAG('git_log_etl', default_args=default_args)

# TODO: Create json config file to store this list of repositories. 
# TODO: Test with more than one repository
# TODO: Find out which folder the clone_task will run in; I want it to be in the top level "repos" directory
repos = [
    'https://github.com/scala/scala.git'
]

clone_template="""
{% for repo in params.repos %}
  git clone {{ repo }}
{% endfor %}
"""
clone_task = BashOperator(task_id='clone_task',
       bash_command=templated_clone_templatecommand,
       params={'repos': repos}
       dag=git_log_etl)

