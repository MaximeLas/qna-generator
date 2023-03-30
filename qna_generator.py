import argparse
import os

import pandas as pd
import numpy as np

from helper_functions import *


''' Set Up - Change these values if needed '''

# directory where pdf files are stored
grants_dir = 'IAF'

# keyword to pdf file map
keyword_to_pdf_file_map = [
    ('Maxime', 'Belize English Proposals 2018-2022_Redacted.pdf'),
    ('Jamaica', 'Jamaica Proposals 2018-2022.pdf'),
    ('Caribbean', 'Eastern Carribean English Proposals 2018-2022.pdf')
]


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        prog = 'Generate Question & Answer',
        description = 'Convert pdf files to txt files and/or generate the relevant Q&A from them',
        epilog = '© Publico')

    # add arguments to the parser object
    parser.add_argument('dir', nargs='?', help='the directory where the pdf & xlsx files are stored')
    parser.add_argument('-no-xlcon', '--no-xlsx-to-csv-conversion',
                        action='store_true', help='do not convert excel files to csv files')
    parser.add_argument('-no-pdfcon', '--no-pdf-to-txt-conversion',
                        action='store_true', help='do not convert pdf files to txt files')
    parser.add_argument('-no-qnagen', '--no-question-answer-generation',
                        action='store_true', help='do not generate the Q&A from the txt files')

    # parse the arguments from the command line
    args = parser.parse_args()

    # check if a directory is specified
    if not args.dir:
        # if no directory is specified, then we will simply use the default directory defined above
        print('Using the default directory: ' + grants_dir)
    else:
        # if a directory is specified, then use it
        grants_dir = args.dir
    
    # excel files
    page_markers_xl = os.path.join(grants_dir, 'page_markers.xlsx')
    question_answer_matching_xl = os.path.join(grants_dir, 'question_answer_matching.xlsx')

    # output directory
    output_dir_name = 'output'
    
    # check if the user wants to convert pdf files to txt files
    if not args.no_pdf_to_txt_conversion:
        ''' Convert PDF to TXT '''

        # check if the user wants to convert excel files to csv files
        if not args.no_xlsx_to_csv_conversion:
        # convert excel to csv
            excel_to_csv(page_markers_xl)

        # read csv file
        df = pd.read_csv(page_markers_xl.replace('.xlsx','.csv'))

        # loop through keyword to pdf file map
        for (keyword, pdf_file) in keyword_to_pdf_file_map:
            # get the relevant column as list from csv file
            column = df[keyword].tolist()

            # get first page number from column and subtract 1 because page numbers start at 0
            first_pages = [int(first_page) - 1 for first_page in column if not np.isnan(first_page)]
            
            # convert pdf to txt
            pdf_to_txt(
                file_name=pdf_file, # pdf file name
                dir_path=grants_dir, # directory where pdf file is stored
                output_dir=output_dir_name, # output directory
                first_pages=first_pages # first page numbers
            )
    
    # check if the user wants to generate Q&A from txt files
    if not args.no_question_answer_generation:
        ''' Generate Q&A from TXT '''

        # check if the user wants to convert excel files to csv files
        if not args.no_xlsx_to_csv_conversion:
            # convert excel to csv
            excel_to_csv(question_answer_matching_xl)

        # read csv file
        df = pd.read_csv(question_answer_matching_xl.replace('.xlsx','.csv'))

        # get path of output directory where txt files are stored
        txt_files_dir = os.path.join(grants_dir, output_dir_name)

        # loop through txt files in output directory
        for file_name in os.listdir(txt_files_dir):
            # check if file is a txt file but not a generated Q&A file
            if file_name.endswith('.txt') and not file_name.endswith('_Q&A.txt'):
                print(f"\n\nGenerate answers from '{file_name}'\n")

                # get path of txt file
                file_path = os.path.join(txt_files_dir, file_name)

                # create empty Q&A file
                answers_file = file_path.replace('.txt','_Q&A.txt')
                open(answers_file, "w").close()

                # loop through rows in csv file
                for _, question_answer_matching_row in df.iterrows():
                    generate_answer_for_question_from_file(
                        file_path=file_path,
                        matching_row=question_answer_matching_row
                    )
