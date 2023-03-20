import os
import re

import fitz
import pandas as pd
import numpy as np


# convert excel to csv
def excel_to_csv(file_excel: str):
    '''Convert excel to csv'''

    # read excel file
    df = pd.read_excel(file_excel)
    # get csv file name
    file_csv = file_excel.replace('.xlsx','.csv')
    # write to csv file
    df.to_csv(file_csv, index=False)


# convert pdf to txt
def pdf_to_txt(
    file_name: str,                 # pdf file name
    dir_path: str = '',             # directory where pdf file is stored
    output_dir: str = '',           # output directory
    first_pages: list[int] = [0]    # first page numbers
):
    '''Convert pdf to txt'''

    # create output directory if it does not exist
    output_dir_path = os.path.join(dir_path, output_dir)
    os.makedirs(output_dir_path, exist_ok=True)

    # open pdf file
    file_pdf_path = os.path.join(dir_path, file_name)
    pdf_doc = fitz.open(file_pdf_path)
    
    for i, first_page in enumerate(first_pages):
        # get first page number of current application and of next application (if it exists)
        first_page_current = first_page
        first_page_next = first_pages[i+1] if i < len(first_pages) - 1 else len(pdf_doc)
        
        text = ''
        # get text from pdf file from first page to last page of current application
        for j in range(first_page_current, first_page_next):
            text += pdf_doc[j].get_text()
        
        # Remove (multiple) empty lines
        text = re.sub('(^\s*\n)+', '', text, flags=re.MULTILINE)
        # remove new line before lowercase letter
        text = re.sub('\n([a-z])', lambda match_obj: match_obj.group(1), text)

        # get output file name (e.g. 'file_name_1.txt') and path (e.g. 'dir_path/output_dir/file_name_1.txt')
        output_file_name = file_name.replace('.pdf',f'_{i}.txt')
        output_file_path = os.path.join(output_dir_path, output_file_name)

        # write text to txt file 
        with open(output_file_path, 'w') as file:
            file.write(text)


def generate_answer_for_question_from_file(
    file_path: str,                     # txt file path
    matching_row: pd.core.series.Series # row containing info about the Q&A (e.g. 'Start After' and 'End Before' regex)
):
    ''' Generate Q&A from TXT '''

    # get 'Start After' and 'End Before' regex from Series
    start_after_regex = matching_row['Start After']
    end_before_regex = matching_row['End Before']

    # get question from Series (if 'Question (Implied)' is not empty, use that, otherwise use 'Question (As Written)')
    question_implied = matching_row['Question (Implied)']
    question = question_implied if question_implied is not np.nan else matching_row['Question (As Written)']
    print(f'\nQuestion:\t\t{question}')

    # get output file path (e.g. 'dir_path/output_dir/file_name_1_Q&A.txt')
    answers_file = file_path.replace('.txt','_Q&A.txt')
    with open(answers_file, 'a') as f:
        # write question and regex to file (for debugging)
        f.write(f'\n{"*"*100}\n') # separator line to separate questions
        f.write(f'Start After\t->\t{start_after_regex}\n') # write 'Start After' regex to file
        f.write(f'End Before\t->\t{end_before_regex}\n\n') # write 'End Before' regex to file
        f.write('-- Question\n' + question + '\n\n') # write question to file
        
        # initialize result variable (will be used to store generated answer or error message)
        result = ''

        try:
            # open file
            with open(file_path, 'r') as file:
                # read text from file
                text = file.read()
                
                # search for start regex in text
                start_after_regex = matching_row['Start After']
                start_after_match = re.search(start_after_regex, text)
                # if regex does not match, raise exception
                if start_after_match is None:
                    raise Exception(f"Did not match 'Start After' regex -> {start_after_regex}")
                # get matched string
                start_after_string = start_after_match.group(0)
                # get start index of matched string
                start_before_idx = text.find(start_after_string)
                # get start index of our generated answer
                answer_start_idx = start_before_idx + len(start_after_string)

                # search for end regex in text (from start index of generated answer)
                end_before_regex = matching_row['End Before']
                end_before_match = re.search(end_before_regex, text[answer_start_idx:])
                # if regex does not match, raise exception
                if end_before_match is None:
                    raise Exception(f"Did not match 'End Before' regex -> {end_before_regex}")
                # get matched string
                end_before_string = end_before_match.group(0)
                # get end index of matched string
                end_before_idx = text.find(end_before_string, answer_start_idx)

                # get generated answer from text and strip leading and trailing whitespace
                result = text[answer_start_idx:end_before_idx].strip()

                # print some info to console (for debugging)
                print(f'Result length:\t\t{end_before_idx - answer_start_idx}')
                print(f"start after regex:\t{start_after_regex}")
                print(f"start after string:\t{start_after_string}")
                print(f"end before regex:\t{end_before_regex}")
                print(f"end before string:\t{end_before_string}")
        except BaseException as e:
            # if exception is raised, store error message in result variable
            result = str(e)

            print(f'Error:\t\t\t{result}') # print error message to console (for debugging)

        # write answer to file (or error message if exception is raised)
        f.write(f'-- Answer\n{result}')


if __name__ == '__main__':
    pass

