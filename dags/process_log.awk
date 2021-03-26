{ 
# run this script with the following command:
#   git log --pretty=format:']},{%n "commit": "%H",%n "abbreviated_commit": "%h",%n "name": "%aN",%n "email": "%aE",%n "date": "%at",%n"files_changed": [' --numstat --no-merges | awk -f ~/Drive/workshop/2-current/2-data\ engineering/1_git_log.awk >> ~/Desktop/almost.json
  
  # this awk script formats the files and number of lines changed from git log's --names-only and --numstat to json
  # this is a post-processing step taken after doing as much json formatting work as can be done in git log itself.
  # So, here we select for lines that do not have json characters i.e. $0 !~/[":]/
  # binary files have numstat of - - instead of numbers, so fields $1 and $2 will be - and - in those cases.

    # 3 fields in case of non rename entries e.g.  "7 6 src/compiler/scala/tools/nsc/typechecker/Typers.scala"
    if (NF==3 && $0 !~/[":]/){
        # binary file
        if($1=="-"){
            printf("{\"lines_added\": null, \"lines_deleted\": null, \"file_path\": \"%s\",\"name_change\": false, \"is_binary_file\": true},\n",$3);
        }
        # text file
        else{
            printf("{\"lines_added\":%s, \"lines_deleted\":%s, \"file_path\": \"%s\",\"name_change\": false, \"is_binary_file\": false},\n",$1,$2,$3);
        }
    } 

    # 5 fields in case of rename entries e.g. "1 1 src/compiler/scala/tools/{nsc => }/tasty/TastyRefs.scala"
    else if (NF==5 && $0 !~/[":]/){
        # binary file
        if($1=="-"){
            printf("{\"lines_added\": null, \"lines_deleted\": null, \"file_path\": \"%s %s %s\",\"name_change\": true, \"is_binary_file\": true},\n",$3,$4,$5);
        }
        # text file
        else{
            printf("{\"lines_added\":%s, \"lines_deleted\":%s, \"file_path\": \"%s %s %s\",\"name_change\": true, \"is_binary_file\": false},\n",$1,$2,$3,$4,$5);
        }
    } 
    # in all other cases, just return the line as-is
    else{
        print $0;
    }
}