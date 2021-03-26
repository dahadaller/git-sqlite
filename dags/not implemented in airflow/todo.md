## Goals

My Goals are to complete the following three projects for my Github:

1. A small project, similar to the [Scala Language Project]((https://learn.datacamp.com/projects/163)), except I take in the github history of  the major github projects:
   - Apache Hadoop (Map Reduce, HDFS)
   - Apache Hive
   - Apache Spark
   - Apache Airflow
   - Luigi
   - for more tools see this github repo: https://github.com/igorbarinov/awesome-data-engineering
2. Take the project from step 1, and turn it into a data pipeline, complete with ETL + Visualization.
   - Extract: Access the data via api, or schedule file downloads from github
   - Translate: Rewrite the translation steps from pandas to apache spark
   - Load: *not sure what to do about load for now. Maybe just an sqlite?* Just needs to be accessible from browser.
   - Scheduling: Use Airflow to schedule the ETL
   - Visualization: Use a Javascript library like D3.js or something built on D3 like Vega.
   - Documentation: Document the architecture in a markdown README file explaining the project. 
3. **A d3.js animation of cellular automaton**: To gain data visualization experience, create a browser-based animation using D3.js similar to the animation shown at these links: 
	- [What is the cellular automaton shown as loading screen on Wolfram Alpha? - Stack Overflow](https://stackoverflow.com/questions/27332460/what-is-the-cellular-automaton-shown-as-loading-screen-on-wolfram-alpha/29168872) 
	-  [javascript - "Progress dots" in D3, Wolfram style - Stack Overflow](https://stackoverflow.com/questions/27880534/progress-dots-in-d3-wolfram-style)
	-  [Cellular Automaton 3457/357/5 - JSFiddle - Code Playground](https://jsfiddle.net/iAmMortos/espncctd/)
4. Finish the remainder of DataCamp's [Data Engineer with Python Track](https://learn.datacamp.com/career-tracks/data-engineer-with-python?version=3).



## Goal 1, 2 & 3 Coursework



- [x] For Goal #1, take the following courses in the [Data Engineer with Python Track](https://learn.datacamp.com/career-tracks/data-engineer-with-python?version=3) from DataCamp:
    - [x] Finish learning to ingest data:
      - [x] [Streamlined Data Ingestion with pandas | DataCamp](https://learn.datacamp.com/courses/streamlined-data-ingestion-with-pandas)
    - [x] Finish the Scala Language Project, along with any prerequisites:

      - [x] [Merging DataFrames with pandas | DataCamp](https://learn.datacamp.com/courses/merging-dataframes-with-pandas)
      - [x] [Data Manipulation with pandas | DataCamp](https://learn.datacamp.com/courses/data-manipulation-with-pandas)
      - [x] [DataCamp Project: The GitHub History of the Scala Language](https://learn.datacamp.com/projects/163)
- [ ] For Goal #3, take the following courses in the [Data Engineer with Python Track](https://learn.datacamp.com/career-tracks/data-engineer-with-python?version=3) from DataCamp:
    - [ ] [Introduction to Airflow in Python | DataCamp](https://learn.datacamp.com/courses/introduction-to-airflow-in-python)
    - [ ] [Introduction to PySpark | DataCamp](https://learn.datacamp.com/courses/introduction-to-pyspark)

    - [ ] [Unit Testing for Data Science in Python | DataCamp](https://learn.datacamp.com/courses/unit-testing-for-data-science-in-python)
    - [ ] [Building Data Engineering Pipelines in Python | DataCamp](https://learn.datacamp.com/courses/building-data-engineering-pipelines-in-python)
    - [ ] [Writing Efficient Python Code | DataCamp](https://learn.datacamp.com/courses/writing-efficient-python-code)
- [ ] For Goal #2, 
    - [ ] read [Eloquent JavaScript](https://eloquentjavascript.net/) up to chapter 8, (can continue reading after project work if you want to continue your deep-dive of javascript.)
    - [ ] Learn D3.js (see [Data Visualization with D3.js Free Code Camp YouTube](https://www.youtube.com/watch?v=_8V5o2UHG0E),   [d3.js - Full Stack Python](https://www.fullstackpython.com/d3-js.html)) 
        - [ ] read eloquent js chapter on promises
        - [ ] make a face with d3.js (see video)
        - [ ] make a bar chart with d3.js (see video)
    
    


## Goal 1 + 2 tasks

Two Questions this project should answer:

1. which files have been changed recently, and by whom? I want to vizualize the current areas of development on the project in question (maybe a pie chart by folder or a stacked line chart?)
2. For a given file, who can I ask about its changes? This would follow the `git log --oneline -M --stat --follow -- src/somefile.ts` command for each file. see [Use --follow option in git log to view a file's history](https://kgrz.io/use-git-log-follow-for-file-history.html)
3. A third (optional) question could be: Who has contributed most to the project in general? This could be useful to make a scoreboard for the github repo. However that would be something to implement when I get more acquainted with javascript. This question could be answered by storing the value of the command `git shortlog -sn --no-merges` see [Some commands to get git commit log statistics for a repository on the command line.](https://gist.github.com/eyecatchup/3fb7ef0c0cbdb72412fc)






### Question 1 tasks

- [x] Python notebook: clean the git log json file
- [x] import json into pandas and separate data into two data frames (one for commits and one for files associated with each commit sha)
- [x] save these two dataframes as a sqlite file
    - when in sqlite you can get a list of which files have been changed recently as follows
        1. select commits where date is greater than some designated date (eg. files changed in last 30 days)
        2. Join files and commits tables on sha
        3. group by filename and aggregate number of changes, then sort by number of changes from greatest to least.
- [x] take the intro to airflow course in datacamp
- [ ] schedule the job to run on mac with airflow (first step to job would be pulling the repo if it's not in a given directory and then running the git log and awk scripts.)
- [ ] read datasette docs to learn how to set up a datasets instance
- [ ] set up a datasette instance to serve the sqlite file on the raspberry pi
    - [ ] this will require resetting the raspberry pi and re-configuring all the dynamic DNS settings nginx configurations etc. while you do this, write down everything you're doing
- [ ] Edit the markdown blog post, and then post to medium, and then post that medium thing on your LinkedIn. 



#### From TextProcessing.md

This command produces the entire commit log for the default branch of the repository, for all files going back to 2003.

```bash
git log --pretty=format:']},{%n "commit": "%H",%n "abbreviated_commit": "%h",%n "name": "%aN",%n "email": "%aE",%n "date": "%at"%n[' --numstat > ~/Desktop/almost.json
```

using awk, replace the first line of almost.json with [{
and replace the last line with }]

Then, for each list of directories in the json objects, wrap each list item in double quotes "", terminate with a comma "," and add encompass the list with "files_changed:[" and "]". 



the first numstat column is the number of added lines and the next is the number of deleted lines.

7       10      src/compiler/scala/tools/nsc/typechecker/PatternTypers.scala
7       6       src/compiler/scala/tools/nsc/typechecker/Typers.scala
5       5       src/reflect/scala/reflect/api/Types.scala
1       4       src/reflect/scala/reflect/internal/Definitions.scala
33      40      src/reflect/scala/reflect/internal/Mode.scala
1       1       src/reflect/scala/reflect/internal/Symbols.scala
0       1       README.md



This command produces the commit log for a specific file (in this case README.MD) and follows it through name changes. it needs to be processed in the same fashion as the output above. 

```bash

git log --pretty=format:'},{%n "commit": "%H",%n "abbreviated_commit": "%h",%n "name": "%aN",%n "email": "%aE",%n "date": "%at"%n ' --numstat --follow README.md 
```


Do not delete this. it's my baby
```bash
git log --pretty=format:']},{%n "commit": "%H",%n "abbreviated_commit": "%h",%n "name": "%aN",%n "email": "%aE",%n "date": "%at",%n"files_changed": [' --numstat --no-merges | awk -f ~/Desktop/j.awk >> ~/Desktop/almost.json
```


I tried my best to do all the pre-processing in bash. there are still 3 corrections to be made with the json

1. trailing commas }, in the file list
2. the end bracket ]
3. the beginning bracket [

I'll look into how to write large files in python again later on. 

https://www.blopig.com/blog/2016/08/processing-large-files-using-python/



### Question 2 tasks:

- [ ] get all repository files in a python list
- [ ] for each file, run `git log —follow` , and then process the output into json or csv (csv is preferred)
- [ ] import into pandas and export to sqlite
- [ ] incorporate into datasette as with previous question

 




## Other Stuff:

- should go over everything that I learned at work about indexes, how to declare effective indexes and that
- in addition to how to creat boyce codd normal form databases, in preparation for data engineering interviews that might come up.
