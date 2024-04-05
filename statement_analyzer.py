from pdfquery import PDFQuery
from lxml import etree
import pandas
from pypdf import PdfReader

class purchase: 
    def __init__(self, date, description1, description2, value, category): 
        self.date = date
        self.description1 = description1
        self.description2 = description2
        self.value = value
        self.category = category

def isDate(string):
    if(len(string) < 9 or len(string) > 10): 
        return False
    for char in string: 
        if(not(char.isdigit() or char == '/' )):
            return False     
    if((string[1] == '/' and string[4] == '/') or (string[2] == '/' and string[5] == '/')): 
        return True

# def isPurchase(string):
#     if(string == 'Purchase'):
#         return True
#     else:
#         return False
    
def isPurchase(string):
    for char in string:
        if(not(char.isdigit() or char == '-' or char =='$' or char == '.' or char == ',')):
            return False
    if(string[0] == '-' and string[1] == '$' and string[(len(string)-3)]=='.'):
        print(len(string))
        return True
    else: 
        return False 



def statementToPurchases(statement):
    purchases = []
    count = 0
    for i in range(len(statement)-5):
        #print(line)
        if(isDate(statement[i]) and statement[i+3] =='Purchase' and isPurchase(statement[i+4]) and isDate()): 
            purchases.append(purchase(statement[i], statement[i+1], statement[i+2], statement[i+4]))
        # if(isWithdrawal(line)): 
        #     print('Withdrawal: ', line)
        #     count+=1
        # if(isDate(line)): 
        #     print(line)
        #     count +=1
        # purchases.append(purchases(date, value, description1, description2, category))
    return purchases

def main():
    pdf = PdfReader('Timmy_Quinn_Secured credit_eStatement.pdf')
    print('Printing text: ')
    text = ''
    for page in pdf.pages: 
        text += page.extract_text()
    statement = text.split('\n')
    
    statementToPurchases(statement)
    # print(statement[0])
    # print(len(statement))
    # for line in statement: 
    #     print(line)

    # lines = text.split('\n')

    # Print the first 5 lines
    # for line_number, line in enumerate(lines[:5], start=1):
    #     print(f"Line {line_number}: {line}")
main()


# def organizeByPurchase():

#def check_purchase




# dollarSigns = 

# left_corner = float(label.attr('x0'))
#bottom_corner = float(label.attr('y0'))
# name = pdf.pq('LTTextLineHorizontal:in_bbox("%s, %s, %s, %s")' % (left_corner, bottom_corner - 30, left_corner+150, bottom_corner)).text()
# print(name); 
##pdf.tree.write('statement.xml', pretty_print = True)




def testFunction(): 
    pdf = PDFQuery('Timmy_Quinn_Secured credit_eStatement.pdf')
    pdf.load()
    print("loaded")
    labels = pdf.pq('LTTextLineHorizontal:contains("Purchase")')
    purchases = 0
    for label in labels:
        # Get the coordinates of the current label
        left_corner = float(label.attrib['x0'])
        bottom_corner = float(label.attrib['y0'])
        # page_number = int(label.getparent().attrib['page_number'])
        print('coordinates: ', left_corner, bottom_corner)
        lxml_element = etree.fromstring(etree.tostring(label))
        print(etree.tostring(lxml_element, pretty_print=True).decode())

        # Find the text near the current label
        # name = pdf.pq('LTTextLineHorizontal:in_bbox("%s, %s, %s, %s")' % (left_corner, bottom_corner - 500, left_corner+50, bottom_corner)).text()
        # print("Purchase: ", purchases)
        # print(name)
        purchases = purchases + 1
    print('Total Purchases: ', purchases)

