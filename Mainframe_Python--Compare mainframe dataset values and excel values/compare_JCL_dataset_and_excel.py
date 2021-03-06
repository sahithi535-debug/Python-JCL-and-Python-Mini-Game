# -*- coding: utf-8 -*-
"""
Created on Sat May 18 13:56:09 2019

@author: NEO
"""

"""This Script Pulls JCL datasets out of mainframe as text file 
and compares specific column values against any specific column data from Excel file.
This is useful for performing analysis and comparing work by pulling out the data from mainframes 
and analysing using Python instead of doing through JCLs.
This logic can be used to analyse 2 JCL datasets or 2 excel files or 2 text files or anything else."""

import getpass
import os
import ftplib
import pandas as pd
import csv

"""setting up variables"""
# give your Host FTP Url
ftp_url = "" 
# takes FTP username as input
user_name = input("Enter FTP username: ") 
# takes FTP password
user_pass = getpass.getpass("Enter User Password: ") 
# give the excel file path that needs to be compared with dataset
excel_path = ""
#takes base path of the script. script will use this path to store other files
base_path = os.path.abspath(os.path.realpath(__file__)) 


def host_data():
    """This function takes the dataset out of Host and saves it as text file. 
    Then, converts the required columns in fixed width text file to Pandas Dataframes and returns the dataframe"""
    #empty list to which which will append the data read from host
    ftp_data = []
    #creates and opens a new text file host_data.txt in base path and open in 'write' mode
    txt_file=open(base_path + "host_data.txt", 'w') 
    try:
        ftp = ftplib.FTP(host = ftp_url, 
                         user = user_name, 
                         passwd = user_pass)
    except ftplib.all_errors as err:
        print(str(err)+ "-Incorrect Login Credentials")
        print("Quitting")
        quit()
    try:
        #replace HLQ with high level qualifier of the dataset within the single quotes.
        ftp.cwd("'HLQ'")
        # replace 'Dataset_Name' with the dataset name without the High Level Qualifier. Data in the dataset is retrieved and each line is appended to ftp_data list.
        ftp.retrlines("RETR Dataset_Name", ftp_data.append)
        #write each value in the ftp_data list to a new line in txt_file
        for line in ftp_data:
            txt_file.write(line + '\n')
        txt_file.close()   #close the text file
        ftp.quit() #quit ftp
    except:
        print("There was some error writing to the text file")
        quit()
    #loads out output host file as dataframe. In the width attribute, give the positions of each column by opening text file in notepad++. In column attributte, give the name for column heades for each column that is mentioned in widhts.
    df_host = pd.read_fwf(base_path + "host_data.txt", 
                          delim_whitespace = False, 
                          dtype = 'str', 
                          widths = [7, 8 , 10] , 
                          skiprows = 1, 
                          header=None, 
                          name = ['Column1_header', 'Column2_header', 'Column3_header'])
    return df_host



def excel_data():
    """ This function reads the Excel file and converts it to dataframe. This function can be modified to read a text file or CSV as well."""
    #read xlsx file, read the sheetname from the excel defined in the excel_path variable
    data_xlsx = pd.read_excel(excel_path , 'sheet_name', index_col =None)
    #convert excel to CSV  with tab as delimiter.
    data_xlsx.to_csv(base_path + "data_csv.csv", encoding = 'utf-8', sep='\t', index=False) 
    #converting CSV to text
    with open(base_path + "data_text.txt", 'w') as text_file: #write to text file
        with open(base_path + "data_csv.csv", 'r') as csv_file: #read the csv file
            #join each elemnt in the row list with a space and a new line character at the end
            [text_file.write(" ".join(row) + '\n') for row in csv.reader(csv_file)]
    #loads out output text file as dataframe. In the width attribute, give the positions of each column by opening text file in notepad++. In column attributte, give the name for column heades for each column that is mentioned in widhts.
    df_excel = pd.read_fwf(base_path + "data_text.txt", 
                           delim_whitespace = False, 
                           dtype = 'str', 
                           widths = [10, 15 ,20], 
                           skiprows = 1, 
                           header=None, 
                           name = ['Column1_header', 'Column2_header', 'Column3_header']) 
    return df_excel
    

def compare(host_df , excel_df):
    """This function compares the host data dataframe and the excel data dataframe which will be returned from host_dat() and excel_data()"""
    # in order to compare two data frames, both the data frames chould have similar column headers. Currently our dataframes hold all the data as rows and columns.
    # from the above two original dataframes, we can take out the specific similar columns that have to be compared.
    # for ex. column name: marks, percentage from dataframe 1st and marks, percentage from 2nd dataframe
    df_host = host_df
    df_excel = excel_df
    #created new dataframe by copying 3 columns from the original dataframe
    df_host_cols = df_host[['marks', 'percentage', 'average']].copy()
    #selecting the same columns from the excel dataframe
    df_excel_cols = df_excel[['marks', 'percentage', 'average']].copy() 
    
    #applying afew transformations to both the datasets to make sure both have the data of same type.
    
    #converts all the values to string if anything else
    df_host_cols = df_host_cols.applymap(str) 
    df_excel_cols = df_excel_cols.applymap(str)
    
    #replace empty values with 000000 so that they can be compared appropriately.
    df_host_cols = df_host_cols.replace('nan','000000') 
    df_excel_cols = df_excel_cols.replace('nan', '000000')
    
    #give the same differnces count based on all the columns.
    difference = df_host_cols[df_excel_cols != df_host_cols] # OR df_diff = df_excel_cols[df_host_cols != df_excel_cols] 
    #gives all records which have same values, i.e matching records
    df_match = df_host_cols.merge(df_excel_cols)
    #gives non matching records
    df_diff = df_host_cols[~ df_host_cols.isin(df_excel_cols).all(axis=1)]
    #print count of total different records
    print("Total differences: ", difference.count())
    #prints matching records, only 5 records at a time
    print("Matching Records: ", df_match.head(5))
    #prints non macthing records, only 5 records at a time
    print("Mismatch Records: ", df_diff.head(5))
            
    

if __name__ == '__main__':
    #calling all the functions
    compare(host_data(), excel_data())
    
    
    