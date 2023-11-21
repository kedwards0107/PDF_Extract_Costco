
from PyPDF2 import PdfFileReader, PdfFileWriter
import re
import pandas as pd
import os

# creates a list of file names
from os import listdir
from os.path import isfile, join
mypath = '/Users/mack/Desktop/Programming/Python/PDF_Extract/pdf_costco/'
path_list = [f for f in listdir(mypath) if isfile(join(mypath, f))]
# removes .DS_Store from list, don't know why it is there
#path_list.pop(20)
print(path_list)

# for each file in list loops through and captures required information
for file in path_list:
    file_path = 'pdf_costco/'+file
    print(file_path)
    pdf = PdfFileReader(file_path)
    txt = pdf.getPage(0).extractText()
    with open('Purchase.txt', 'w') as f:
        txt = pdf.getPage(0).extractText()
        f.write(txt)
        f.close()
    df = pd.read_csv('export.csv')
    # print(df)
    order_number = re.compile(r'[A-Z0-9]{3}-\d{7}-\d{7}')
    order_date = re.compile(r'(Order Placed: +)(\w*.[0-9]+,.\d\d\d\d)')
    item_desc = re.compile(r'[0-9] of.+\w*')
    item_price = re.compile(r'(Condition: New)(\$)([0-9]+(.[0-9]+)?)')
    subtotal = re.compile(r'(Item\(s\) Subtotal:.)+(\$)([0-9]+(.[0-9]+)?)')
    discount = re.compile(r'.-(\$)([0-9]+(.[0-9]+)?)')
    giftcard = re.compile(r'(Gift Card Amount:.-)(\$)([0-9]+(.[0-9]+)?)')
    shipping = re.compile(r'(Shipping & Handling:.)+(\$)([0-9]+(.[0-9]+)?)')
    try:
        discount_value = -(float(discount.search(txt).group(2)))
    except:
        discount_value = 0
    try:
        giftcard_value = float(giftcard.search(txt).group(3))
    except:
        giftcard_value = 0
    try:
        shipping_value = float(shipping.search(txt).group(3))
    except:
        shipping_value = 0
    total_b4_tax = re.compile(r'(Total before tax:.)(\$)([0-9]+(.[0-9]+)?)')
    estimated_tax = re.compile(r'(Estimated tax to be collected:.)(\$)([0-9]+(.[0-9]+)?)')
    grand_total = re.compile(r'(Grand Total:.)(\$)([0-9]+(.[0-9]+)?)')
    each_item = item_desc.finditer(txt)
    ind_price = item_price.finditer(txt)
    order = order_number.search(txt).group(0)
    order_date_value = order_date.search(txt).group(2)
    subtotal_value = float(subtotal.search(txt).group(3))
    total_b4_tax_value = float(total_b4_tax.search(txt).group(3))
    estimated_tax_value = float(estimated_tax.search(txt).group(3))
    grand_total_value = float(grand_total.search(txt).group(3))

    # dictionary to populate dataframe
    purchases = { "order date": [],"item description": [], "item price": [], "order number": [], "subtotal": [], "discount": [], "shipping":[], "total before tax": [], "estimated tax": [],"gift card": [], "grand total": [], "is_Multiple": []}

    # For each item purchased add to item description in purchases dictionary
    for each in each_item:
        item = each.group(0)
        purchases['item description'].append(item)
        
    # For each item price add to item price, order number, order date and blank values for columns for total line in purchases dictionary. if multiple items in order creates a boolean is_Multiple yes by removing last is_Multiple and replacing it with yes 
    i = 0
    for ind in ind_price:
        price =ind.group(3)
        conv_price = float(price)
        purchases['item price'].append(conv_price)
        purchases['order number'].append(order)
        purchases['order date'].append(order_date_value)
        if i == 0:
            purchases['subtotal'].append(subtotal_value)
            purchases['discount'].append(discount_value)
            purchases['shipping'].append(shipping_value)
            purchases['total before tax'].append(total_b4_tax_value)
            purchases['estimated tax'].append(estimated_tax_value)
            purchases['gift card'].append(giftcard_value)
            purchases['grand total'].append(grand_total_value)
            purchases['is_Multiple'].append("no")
            i = 1
        else:
            purchases['is_Multiple'].pop()
            purchases['is_Multiple'].append("yes")
            purchases['subtotal'].append("")
            purchases['discount'].append("")
            purchases['shipping'].append("")
            purchases['total before tax'].append("")
            purchases['estimated tax'].append("")
            purchases['gift card'].append("")
            purchases['grand total'].append("")
            purchases['is_Multiple'].append("yes")

    
    
    # Creates a total line to show actual amount paid with taxes, shipping, discounts, etc.
    # purchases['item description'].append("TOTAL")   
    # purchases['item price'].append(0)
    # purchases['order number'].append(order)
    # purchases['order date'].append(order_date_value)   
    # purchases['subtotal'].append(subtotal_value)
    # purchases['discount'].append(discount_value)
    # purchases['shipping'].append(shipping_value)
    # purchases['total before tax'].append(total_b4_tax_value)
    # purchases['estimated tax'].append(estimated_tax_value)
    # purchases['gift card'].append(giftcard_value)
    # purchases['grand total'].append(grand_total_value)

    df2 = pd.DataFrame(purchases)
  
    df3 = pd.concat([df, df2])
    #print(df)
    df3.to_csv('export.csv', index=False)
