import requests
import pandas as pd

commits_dict = {}
files_list = []

page = 1
page_size = 100

api_call_count = 0

over_300 = []

while True:
    api_call_count += 1
    commits = requests.get(
        'https://api.github.com/repos/scala/scala/commits',
        params={
            'per_page' : page_size,
            'page': page,
            'since': '2020-07-09T14:32:30Z', # ISO 8601 time format, need to be able to provide this argument in a variable to generate data for each month.
        },
        auth=('dahadaller','113c80e67b7214d934ace34bc9950b34b7dd4242'), #TODO: delete this line and use env file. do not commit.
        headers={'Accept': 'application/vnd.github.v3.text-match+json'}
    )
    
    # figure out how to do better error checking here so that we only proceed past this point if everything has been retrieved as needed.
    commits_json = commits.json()
    
    if not commits_json:
        print('no more data')
        break
        
    else:
        
        for i in range(len(commits_json)):
            
            commit_sha = commits_json[i]['sha']
            
            # collect user commit data into dictionary
            commits_dict[commit_sha] = {
                'name': commits_json[i]['commit']['author']['name'],
                'email': commits_json[i]['commit']['author']['email'],
                'date': commits_json[i]['commit']['author']['date']                
            }
            
            # collect commit file data into separate dictionary, after additional API request
            api_call_count += 1
            files = requests.get(
                f'https://api.github.com/repos/scala/scala/commits/{commit_sha}',
                auth=('dahadaller','113c80e67b7214d934ace34bc9950b34b7dd4242'), #TODO: delete this line and use env file. do not commit.
                headers={'Accept': 'application/vnd.github.v3.text-match+json'}
            )
            
            files_json = files.json()['files']
            
            # if a commit has over 300 changed files, the list of files will be paginated
            # this list is to see how often that happens
            if len(files_json) == 300:
                over_300.append(commit_sha)
            
            for file in files_json:
                
                files_list.append(
                    {
                        'commit_sha': commit_sha,
                        'file_sha': file['sha'],
                        'filename': file['filename'],
                        'additions': file['additions'],
                        'deletions': file['deletions'],
                        'changes': file['changes']
                    }
                )
        
    print(page,len(commits_dict), len(files_list))
    page += 1
    
    
commits_df = pd.DataFrame.from_dict(commits_dict, orient='index')
commits_df.index.name = 'commit_sha'

files_df = pd.DataFrame(files_list)

print(api_call_count)
print(over_300)