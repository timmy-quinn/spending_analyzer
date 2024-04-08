from pdfquery import PDFQuery
from lxml import etree
import pandas
from pypdf import PdfReader
import json
import csv

class purchase:
    def __str__(self):
        return f"Date: {self.date}\nDesc1: {self.description1}\nDesc2: {self.description2}\nValue: {self.value}\nCategory: {self.category}"
    def __init__(self, date, description1, description2, value, category = None): 
        self.date = date
        self.description1 = description1
        self.description2 = description2
        self.value = value
        self.category = category

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
        value = float(purchase[2:])
    except: 
        print(f"Error: Could not convert '{purchase}' to float")
        return None
    else: 
        return value

# Converts
def statementToPurchases(statement):
    purchases = []
    count = 0
    for i in range(len(statement)-5):
        if(isDate(statement[i]) and statement[i+3] =='Purchase' and isPurchase(statement[i+4]) and isDate(statement[i+5])):
            # print('Purchase ', i) 
            # print((statement[i]))
            # print((statement[i+1]))
            # print((statement[i+4]))
            value = formatValue(statement[i+4])
            purchases.append(purchase(statement[i], statement[i+1], statement[i+2], value))
    
    # print(len(purchases))
    return purchases

# def removePageNumbers(text, pgNum, pgCount): 
#     pgStr = f'Page {pgNum + 1} of {pgCount}'
#     for line in text: 
#         if(line[0:len(pgStr)] == pgStr):
#             line = line[len(pgStr) + 1 : len(line)]
            

def getStatement(pdf):
    text = ''
    statement = []
    for i in range(len(pdf.pages)): 
        page = pdf.pages[i].extract_text()
        text = page.split('\n')
        statement +=text
    return statement

def requestCategory(purchase):
    while True:
        response = input('\n********************************************************************\n' 
                         'Groceries = gr, Gas = gas, Eating out = e, Fitness = f, \n'
                         'Subscriptions = s, Car maintenance = c, Miscellanous = m\n'
                         'Transportation = t\n'
                         '********************************************************************\n'
                         f'\nWhat categrory does the {purchase.value} purchase at {purchase.description1} fall into?\n')
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

def printPercentages(totals): 
    for key, value in list(totals.items())[:-1]: 
        print(f"{key} : {round((value/(totals['Total']) *100), 2)}%")
    print(f"Total: totals['Total']")
        
def main():
    with open('statement.txt', 'r') as file: 
        statement_name = file.read()
    pdf = PdfReader(statement_name)
    print('Printing text: ')
    statement = getStatement(pdf)
    purchases = statementToPurchases(statement)
    # for line in statement:
    #     print(line)
    # print(text)

    filename = 'categories.json'

    with open(filename, 'r') as file: 
        purchDict = json.load(file)
    assignCategories(purchases, purchDict)

    with open(filename, 'w') as json_file:
        json.dump(purchDict, json_file, 
                            indent=4,  
                            separators=(',',': '))
        
    totals = getSpending(purchases)

    printPercentages(totals)

    # the result is a JSON string:

        
    

    # print(statement[0])
    # print(len(statement))
    # for line in statement: 
    #     print(line)

    # lines = text.split('\n')

    # Print the first 5 lines
    # for line_number, line in enumerate(lines[:5], start=1):
    #     print(f"Line {line_number}: {line}")
main()