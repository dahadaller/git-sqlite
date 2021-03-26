# python3 ~/Drive/workshop/2-current/2-data\ engineering/2_to_json.py


import pathlib

invalid_json_file = pathlib.Path.home() / 'Desktop' / 'almost.json'
valid_json_file = pathlib.Path.home() / 'Desktop' / 'valid.json'


# find line indices of invalid that should be 
# edited before writing to valid. These just 
# looking for lines between square brackets [] using a stack to remove the 
# comma of the last element in each list.
# also want to remove the comma from the last line
with invalid_json_file.open(mode='r') as invalid:

    comma_lines = set()
    last_line_number = 0

    stack = []
    between_brackets = False
    
    for line_number, line in enumerate(invalid):

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


# edit and write lines to valid
with invalid_json_file.open(mode='r') as invalid, valid_json_file.open(mode='w') as valid:
    
    # correct top-level bracket on first line
    # and add { for furst element
    valid.write('[{\n')
    
    for line_number, line in enumerate(invalid):

        if line_number == 0:
            continue

        elif line_number in comma_lines:
            comma_index = line.rfind(',')
            valid.write(line[:comma_index])
            comma_lines.remove(line_number)
        else:
            valid.write(line)
    
    # correct top-level bracket on last line
    valid.write(']}]')


import json

with valid_json_file.open(mode='r') as valid:
    data = json.load(valid)


