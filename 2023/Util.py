import configparser
import os
import re

import pypdf
from pypdf import PdfReader

import fpdf #pip3 intall fpdf

def writePdfFile (file):


    pdf = fpdf.FPDF(format='letter')  # pdf format
    pdf.add_page()  # create new page
    pdf.set_font("Arial", size=18)  # font and textsize
    pdf.cell(200, 10, txt="       #STMT", ln=1, align="L")
    pdf.cell(200, 10, txt="       ", ln=2, align="L")

    pdf.set_font("Arial", size=12)  # font and textsize

    counter = 4
    with open(file, 'r') as f:
        for line in f.readlines():
            pdf.cell(200, 7, txt=line, ln=counter, align="L")
            counter +=1

    pdf.output(configObjToArray('DIRS', '.editconfig')['output_folder'] + '\\' + 'STMT.pdf')

def configObjToArray (option , file):
    #   CREATE OBJECT
    arr = {}
    config_file = configparser.ConfigParser()
    conf = configparser.ConfigParser()
    #   READ CONFIG FILE
    config_file.read(file)
    for i in config_file.options(option):
        arr[i]=config_file.get(option , i)
    return arr

def buildAndSearchFile (dir , file):
    if file.exist():
        i =0
    return
#config file has attributes that have multipule options
def extractArrFromStringConfigFile (str):

    str = str.replace(' ', '')
    if not re.match(r'.+[\:,].+[,.+\:.+,.+\:.+]*' , str):
        # print('error: pattern unknown')
        return None

    b = {}
    a = str.split(',')
    for j in a:
        c = j.split(':')
        b[c[0]] = c[1]

    return  b



def fieldsDumper(pdfFile, writeFile = False):
    reader = PdfReader(pdfFile)
    fields = reader.get_fields()
    pdfOutFile = pdfFile.split('.')
    pdfOutFile1 = pdfOutFile[0] + '_fields'

    if writeFile:
        with open(pdfOutFile1 , "w") as output_stream:
            for i in fields.keys():
                output_stream.write(i + '\n')
            output_stream.write('[PDF_SRC]\n' + 'path = '+ pdfFile)
            output_stream.close()

        return pdfFile

    else:
        return fields.keys()


# This method is used to compare two 1040 files, in order to get the diffrences.
#NOTE it gets files of Compiled PDF, [the Output-beta of ]
def comparefiles (file1 , file2):

    arr1 = []
    arr2 = []
    file1 = file1.replace(' ', '')
    file2 = file2.replace(' ', '')

    if file1.endswith('.pdf'):
        if file2.endswith('.pdf'):
            arr1=fieldsDumper(file1)
            arr2=fieldsDumper(file2)
        else:
            print('Error: put PDF files OR _fields files!')

    else:
        if not file2.endswith('pdf'):
            print('Error: put PDF files OR _fields files!')
        else:
            with open(file1, "r" ) as output_stream1:
                arr1 = output_stream1.readlines()
            with open(file2, "r") as output_stream2:
                arr2 = output_stream2.readlines()


    count = 0
    for i in arr1:
        for j in arr2:
            if i == j:
                print('[V] ' +i)
                count+=1
    print('Common fields #: ' +count.__str__())



def findFields (fieldToMatch, line):

    m = re.search(fieldToMatch , line)
    if m:
        return line
    else:
        return None



###'''
#This function use after dumping PDF's lines, to create fields name
# automatically. By simbolyzing the line with ':' will give the field
# name, and '#' gives the notation like:
#
# form1[0].Page1[0].f1_02[0]  :ssn    #ssn
#
# will generates this line:
# #ssn
# ssn = form1[0].Page1[0].f1_02[0]
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# '''
def createFieldsFile (fileName):
    ##fieldsDumper(file, True)
    fieldsList =[]
    with open(fileName+'_f' , "w") as output_stream:
        output_stream.write('[FIELDS]\n')
        st = ''
        with open(fileName, 'r') as inFile:
            for line in inFile.readlines():
                line = line.replace(' ', '')
                if findFields('.:.[.#.]?' , line) not in [None]:

                    s = line.split('#')
                    if len(s) > 1:
                        output_stream.write('#'+s[1])
                        s=s[0]
                    else:
                        s[0]=s[0].split('\n')
                        s = s[0][0]

                    s=s.split(':')
                    # s[0].replace (':' , '=')
                    fieldsList.append(s[1])
                    s = s[1] + ' = ' + s[0]+'\n\n'
                    output_stream.write(s)
                    print(s)
            output_stream.write('\n\n\[FIELDS_TO_PASTE]\n\n\n')
            for i in fieldsList:
                output_stream.write('fields [\''+ i +'\'] : \n')



# fieldsDumper('C:\\Users\\aman\\Documents\\GitHub\\, True)
# comparefiles ('C:\\Users\\aman\\PycharmProjects\\1040_AutoScript@2023\\PDFs\\f1040s3.pdf ', 'C:\\Users\\aman\\PycharmProjects\\1040_AutoScript@2023\\PDFs\\22\\f1040s3.pdf ' )
# fieldsDumper ( 'C:\\Users\\aman\\PycharmProjects\\1040_AutoScript@2023\\PDFs\\f1116.pdf' , True)

# writePdfFile ('C:\\Users\\aman\\PycharmProjects\\1040_AutoScript@2023\\1040_2023_files-beta\\Declarations_2023.txt')