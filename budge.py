from pypdf import PdfReader
import json
import matplotlib.pyplot as plt
import numpy as np
import csv
from tkinter import Tk     # from tkinter import Tk for Python 3.x
from tkinter.filedialog import askopenfilename
import shutil
import xlsxwriter
import os

destPath = ''

class purchase:
    def __str__(self):
        return f"Date: {self.date}\nDesc1: {self.description1}\nDesc2: {self.description2}\nValue: {self.value}\nCategory: {self.category}"
    def __init__(self, date, description1, description2, value, category = None): 
        self.date = date
        self.description1 = description1
        self.description2 = description2
        self.value = value
        self.category = category

months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']

# Checks if string is in the date format in the document
def isDate(string):
    if(len(string) < 9 or len(string) > 10): 
        return False
    for char in string: 
        if(not(char.isdigit() or char == '/' )):
            return False     
    if((string[1] == '/' and string[4] == '/') or (string[2] == '/' and string[5] == '/')): 
        return True
    
# Checks if string is in purchase format from the document 
def isPurchase(string):
    for char in string:
        if(not(char.isdigit() or char == '-' or char =='$' or char == '.' or char == ',')):
            return False
    if(string[0] == '-' and string[1] == '$' and string[(len(string)-3)]=='.'):
        return True
    else: 
        return False 

# Removes the -$ from the front of the value string
def formatValue(purchase): 
    try:
        purchase = purchase.replace(',', '')
        purchase = purchase.replace('-$', '')
        value = float(purchase)
    except: 
        print(f"Error: Could not convert '{purchase}' to float")
        return None
    else: 
        return value

# Converts
def getPurchases(statement):
    purchases = []
    for i in range(len(statement)-5):
        if(isDate(statement[i]) and statement[i+3] =='Purchase' and isPurchase(statement[i+4]) and isDate(statement[i+5])):
            value = formatValue(statement[i+4])
            purchases.append(purchase(statement[i], statement[i+1], statement[i+2], value))
    
    # print(len(purchases))
    return purchases

def getStatement(pdf):
    text = ''
    statement = []
    for i in range(len(pdf.pages)): 
        page = pdf.pages[i].extract_text()
        text = page.split('\n')
        statement +=text
    return statement

def formatMonth(statementPeriod):
    global months

    for month in months: 
        if(statementPeriod.find(month) != -1): 
            return '_' + statementPeriod[0:len(month)] + '_' + statementPeriod[len(month)+1:]
    return None
    

def dateToString(date):
    monthNumber = ''
    global months
    for c in date: 
        if(c == '/'): 
            return months[int(monthNumber) - 1] + date[-2:]
        else: 
            monthNumber += c
    return 'Unknown'
    

def getMonth(statement, purchases):
    for i in range(len(statement)): 
        print(statement[i])
        if(statement[i] == 'Statement period' and i < len(statement)):
            print(f'Month: {statement[i+1]}')
            return formatMonth(statement[i+1])
    purchaseDates = {}
    for purchase in purchases: # This is a just in case, if the chime format changes 
        purchaseDates[dateToString(purchase.date)]
    
    return max(purchaseDates, key = purchaseDates.get())

def requestCategory(purchase):
    while True:
        response = input('\n********************************************************************\n' 
                         'Groceries = gr, Gas = gas, Eating out = e, Fitness = f, \n'
                         'Subscriptions = s, Car maintenance = c, Transportation = t, \n'
                         'Fun = f, Books = b, Miscellanous = m\n'
                         '********************************************************************\n'
                         f'\nWhat categrory does the {purchase.value} purchase at {purchase.description1} on {purchase.date} fall into?\n')
        match response: 
            case 'gr':
                return 'Groceries'
            case 'gas': 
                return 'Gas'
            case 'e': 
                return 'Eating out'
            case 'f': 
                return 'Fitness'
            case 's': 
                return 'Subscriptions'
            case 'c': 
                return 'Car maintenance'
            case 'm': 
                return 'Miscellaneous'
            case 't': 
                return 'Transportation'
            case 'f':
                return 'Fun'
            case 'b': 
                return 'Books'
            case _: 
                print("Incorrect input, please try again")

def assignCategories(purchases, purchDict): 
    # https://howtodoinjava.com/python-json/append-json-to-file/#:~:text=Steps%20for%20Appending%20to%20a,object%20into%20the%20original%20file. 
    for purchase in purchases: 
        if not (purchase.description1 in purchDict):
            purchDict.update({purchase.description1 : requestCategory(purchase)})
        purchase.category = purchDict[purchase.description1]

def getSpending(purchases):
    totals = {}
    allSpending =  0
    for purchase in purchases: 
        if not (purchase.category in totals): 
            totals.update({purchase.category : purchase.value})
        else: 
            totals[purchase.category] +=purchase.value
        allSpending += purchase.value

    totals.update({'Total': allSpending})
    return totals

def generateXLSXFiles(percentages, totals, date): 
    global destPath
    workbook = xlsxwriter.Workbook(destPath + date + '.xlsx')
    worksheet = workbook.add_worksheet()

    # Start from the first cell. Rows and columns are zero indexed.
    textCol = 0
    percentCol = 1
    totalCol = 2

    worksheet.write(0, 0, f'Spending for {date}')
    row = 1
    # Iterate over the data and write it out row by row.
    for key, value in list(percentages.items())[:-1]:
        worksheet.write(row, textCol,     key)
        worksheet.write(row, percentCol, value)
        worksheet.write(row, totalCol, f'${totals[key]}')
        row += 1
    
    # Write a total using a formula.
    worksheet.write(row, textCol, 'Total')
    worksheet.write(row, totalCol, f"${totals}['Total']")

    workbook.close()


def generateOutputs(totals, date):
    percentages = {}
    for key, value in list(totals.items())[:-1]: 
        percent = round((value/(totals['Total']) *100), 2)
        percentages[key] = int(percent * 100)
        # categories.append(key)
        # percentages.append(int(percent*100))
    for key,value in percentages.items(): 
        print(f"{key} : {value}%")
    print(f"Total: {round(totals['Total'], 2)}")

    generateXLSXFiles(totals, percentages, date)

    plt.pie(percentages.values(), labels = percentages.keys())
    plt.show()



def getFileName(): 
    attempts = 0
    file = ''
    while attempts < 3: 
        attempts +=1

        Tk(screenName = 'Budget').withdraw()
        file = askopenfilename()
        if(file == ''): 
            print('No file selected. Please select a file.')
        else:
            return file

    return file

def moveRenameFile(file, destPath, append):

    cur_name = os.path.basename(file)
    cur_name, extension = os.path.splitext(cur_name)
    if(cur_name[-len(append):] != append):
        destination = destPath + cur_name + append + extension
    else: 
        destination = destPath + cur_name + extension
    shutil.move(file, destination)
    if os.path.exists(destination): 
        print(f'File moved from {file} to {destination}')
    else: 
        print('Error. Cannot move file')





        
def main():
    global destPath
    filePath = getFileName()
    
    statement = getStatement(PdfReader(filePath))
    purchases = getPurchases(statement)
    # for line in statement:
    #     print(line)
    # print(text)

    catFile = 'categories.json'

    with open(catFile, 'r') as file: 
        purchDict = json.load(file)
    assignCategories(purchases, purchDict)

    with open(catFile, 'w') as json_file:
        json.dump(purchDict, json_file, 
                            indent=4,  
                            separators=(',',': '))
        
    totals = getSpending(purchases)

    with open('dest_path.txt', 'r') as file:  
        destPath = file.read()

    monthYear = getMonth(statement, purchases)
    moveRenameFile(filePath, destPath, monthYear)  
    generateOutputs(totals, monthYear)

    # print(statement[0])
    # print(len(statement))
    # for line in statement: 
    #     print(line)

    # lines = text.split('\n')

    # Print the first 5 lines
    # for line_number, line in enumerate(lines[:5], start=1):
    #     print(f"Line {line_number}: {line}")
main()