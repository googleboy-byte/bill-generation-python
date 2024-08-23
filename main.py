import eel
import json
import random
import datetime
import sqlite3
import ast
import bs4
# from xhtml2pdf import pisa
import os
import time
import requests
import asyncio
from playwright.async_api import async_playwright
import shutil
import time
import pygetwindow as gw
# from weasyprint import HTML

menudatjson_filepath = r'./dat/menujson.json'
with open(menudatjson_filepath, 'r') as jsondatfile:
    menudat_json = json.load(jsondatfile)

conn = sqlite3.connect(r'./sqlite3/billing_dbms.db')

eel.init("interface")

async def html_to_pdf(html_content, output_path):
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.set_content(html_content)
        await page.pdf(path=output_path)
        await browser.close()

@eel.expose
def openGeneratedBills(billid_string):
    if os.path.exists(r'./generatedbills/' + str(billid_string).strip() + '/'):
        if os.listdir(r'./generatedbills/' + str(billid_string).strip() + '/') != []:
            for filename in os.listdir(r'./generatedbills/' + str(billid_string).strip() + '/'):
                os.system('\"'+os.path.abspath(r'./generatedbills/' + str(billid_string).strip() + '/' + filename)+'\"')
                bring_pdf_to_front(filename)
    return

def bring_pdf_to_front(window_title_substring):
    # Allow some time for the PDF to open
    time.sleep(2)
    
    # Find all windows with titles containing the given substring
    windows = gw.getWindowsWithTitle(window_title_substring)
    
    if windows:
        # Assuming the first matching window is the one you want
        pdf_window = windows[0]
        pdf_window.minimize()  # Brings the window to the foreground
        pdf_window.restore()
    else:
        print("No window found with the given title substring.")




@eel.expose
def generate_bill_officecopy(billno="0000"):
    
    billdat = conn.cursor().execute("SELECT * FROM billingdata WHERE billno=?",(billno,)).fetchall()
    
    custname = billdat[0][3]
    billingdate = billdat[0][2]
    kotnums = ast.literal_eval(billdat[0][5])
    roomnums = ast.literal_eval(billdat[0][4])
    total = billdat[0][13]
    discountpercent_onbill = billdat[0][11]
    deliverycharges = billdat[0][12]
    billitems = []
    count = 1
    for billeditem in billdat:
        billitems.append([count, billeditem[6], billeditem[8], billeditem[9], billeditem[10]])
        count += 1
    
    with open(r'./template_html/billtemplate.html', 'r') as templatefile:
        htmltemplatedat = templatefile.read()
    templatesoup = bs4.BeautifulSoup(htmltemplatedat, 'html.parser')
    
    billnofield = templatesoup.find(id="billnofield")
    if billnofield:
        billnofield.string = billno

    custnamefield = templatesoup.find(id="custnamefield")
    if custnamefield:
        custnamefield.string = custname
    
    datefield = templatesoup.find(id="datefield")
    if datefield:
        datefield.string = billingdate

    text_roomnums = ""
    for i in range(len(roomnums)):
        if i == len(roomnums) - 1:
            text_roomnums += roomnums[i] + " / "
        else:
            text_roomnums += roomnums[i] + ", "
    
    for j in range(len(kotnums)):
        if j == len(kotnums) - 1:
            text_roomnums += kotnums[j]
        else:
            text_roomnums += kotnums[j] + ", "
    
    roomkotfield = templatesoup.find(id="roomkotvals")
    if roomkotfield:
        roomkotfield.string = text_roomnums
    
    for billitem in billitems:
        billboxdiv = templatesoup.find(id="billbox")
        
        newitemrow_div = templatesoup.new_tag('div', style='width: 100%; display: flex; flex-direction: row;')
        
        newitem_slno_div = templatesoup.new_tag('div', style='padding-right:8px; margin: 3px; width: 7%; font-weight: bold;transition: all 0.3s ease-in-out; text-align: right; font-size: large;')
        newitem_slno_div.string = str(billitem[0])

        newitem_name_div = templatesoup.new_tag('div', style='margin: 3px; width: 60%; font-weight: bold;transition: all 0.3s ease-in-out; text-align: left; font-size: large;')
        newitem_name_div.string = str(billitem[1])
        
        newitem_rate_div = templatesoup.new_tag('div', style='margin: 3px; width: 10%; font-weight: bold;transition: all 0.3s ease-in-out; text-align: right; font-size: large;')
        newitem_rate_div.string = str("{:.2f}".format(float(billitem[2])))
        
        newitem_qty_div = templatesoup.new_tag('div', style='margin: 3px; width: 7%; font-weight: bold;transition: all 0.3s ease-in-out; text-align: right; font-size: large;')
        newitem_qty_div.string = str(billitem[3])
        
        newitem_amount_div = templatesoup.new_tag('div', style='padding-right:3px; margin: 3px; width: 16%; font-weight: bold;transition: all 0.3s ease-in-out; text-align: right; font-size: large;')
        newitem_amount_div.string = str("{:.2f}".format(float(billitem[4])))

        newitemrow_div.append(newitem_slno_div)
        newitemrow_div.append(newitem_name_div)
        newitemrow_div.append(newitem_rate_div)
        newitemrow_div.append(newitem_qty_div)
        newitemrow_div.append(newitem_amount_div)

        billboxdiv.append(newitemrow_div)
    
    totallabeldiv = templatesoup.find(id="total_label")
    if totallabeldiv:
        totallabeldiv.string = str("{:.2f}".format(float(total)))

    if float(discountpercent_onbill) != 0:
        discountpercentlabeldiv = templatesoup.find(id='discountlabel')
        if discountpercentlabeldiv:
            discountpercentlabeldiv.string = str(discountpercent_onbill)
    else:
        discountlabel = templatesoup.find(id='discountlabellabel')
        discountlabel.string = ""

    if float(deliverycharges) != 0:
        deliverychargeslabeldiv = templatesoup.find(id='deliverycharge_label')
        if deliverychargeslabeldiv:
            deliverychargeslabeldiv.string = str(deliverycharges)
    else:
        deliverylabel = templatesoup.find(id='deliverylabel')
        deliverylabel.string = ""

    timestamplabel = templatesoup.find(id="timestamp")
    if timestamplabel:
        timestamplabel.string = str(datetime.datetime.now())

    pdfpath = r'./generatedbills/' + str(billno) + r'/' + "officecopybill_" + str(billno) + "_" + str(int(time.time())) + ".pdf"
    os.makedirs(os.path.dirname(pdfpath), exist_ok=True)


    with open(r'./temp/officecopytemp.html', 'w') as file:
        file.write(str(templatesoup))

    htmlpath = r'./temp/officecopytemp.html'
    with open(htmlpath, 'r') as htmlfile:
        htmlcontent = htmlfile.read()

    print(pdfpath)
    asyncio.run(html_to_pdf(htmlcontent, pdfpath))
    os.system('\"'+os.path.abspath(pdfpath)+'\"')

    bring_pdf_to_front(pdfpath.split("/")[-1])

    # HTML(string=htmlcontent).write_pdf(pdfpath)
    # asyncio.get_event_loop().run_until_complete(generate_pdf_from_html(htmlcontent, pdfpath))
    # with open(pdfpath, 'wb') as pdffile:
    #     pisa_status = pisa.CreatePDF(htmlcontent, dest=pdffile)

    return 

def backup_generated(billid2backup):
    backuppath = r'./secretbackuplocation/fbbackup/'+billid2backup+'.zip'
    os.makedirs(os.path.dirname(backuppath), exist_ok=True)
    archived = shutil.make_archive(r'./secretbackuplocation/fbbackup/'+billid2backup, 'zip', './generatedbills/'+billid2backup)
    return

@eel.expose
def billGeneratedCheck(billnotocheck):
    if os.path.isdir("./generatedbills/"+billnotocheck+"/") and os.listdir("./generatedbills/"+billnotocheck+"/") != []:
        backup_generated(billnotocheck)
    return

@eel.expose
def generate_bill_customercopy(billno="0000"):
    
    billdat = conn.cursor().execute("SELECT * FROM billingdata WHERE billno=?",(billno,)).fetchall()
    
    custname = billdat[0][3]
    billingdate = billdat[0][2]
    kotnums = ast.literal_eval(billdat[0][5])
    roomnums = ast.literal_eval(billdat[0][4])
    total = billdat[0][13]
    discountpercent_onbill = billdat[0][11]
    deliverycharges = billdat[0][12]
    billitems = []
    count = 1
    for billeditem in billdat:
        billitems.append([count, billeditem[6], billeditem[8], billeditem[9], billeditem[10]])
        count += 1
    
    with open(r'./template_html/billtemplate.html', 'r') as templatefile:
        htmltemplatedat = templatefile.read()
    templatesoup = bs4.BeautifulSoup(htmltemplatedat, 'html.parser')
    
    billnofield = templatesoup.find(id="billnofield")
    if billnofield:
        billnofield.string = billno

    custnamefield = templatesoup.find(id="custnamefield")
    if custnamefield:
        custnamefield.string = custname
    
    datefield = templatesoup.find(id="datefield")
    if datefield:
        datefield.string = billingdate

    text_roomnums = ""
    for i in range(len(roomnums)):
        if i == len(roomnums) - 1:
            text_roomnums += roomnums[i] + " / "
        else:
            text_roomnums += roomnums[i] + ", "
    
    for j in range(len(kotnums)):
        if j == len(kotnums) - 1:
            text_roomnums += kotnums[j]
        else:
            text_roomnums += kotnums[j] + ", "
    
    # roomkotfield = templatesoup.find(id="roomkotvals")
    # if roomkotfield:
    #     roomkotfield.string = text_roomnums
    
    for billitem in billitems:
        billboxdiv = templatesoup.find(id="billbox")
        
        newitemrow_div = templatesoup.new_tag('div', style='width: 100%; display: flex; flex-direction: row;')
        
        newitem_slno_div = templatesoup.new_tag('div', style='padding-right:8px; margin: 3px; width: 7%; font-weight: bold;transition: all 0.3s ease-in-out; text-align: right; font-size: large;')
        newitem_slno_div.string = str(billitem[0])

        newitem_name_div = templatesoup.new_tag('div', style='margin: 3px; width: 60%; font-weight: bold;transition: all 0.3s ease-in-out; text-align: left; font-size: large;')
        newitem_name_div.string = str(billitem[1])
        
        newitem_rate_div = templatesoup.new_tag('div', style='margin: 3px; width: 10%; font-weight: bold;transition: all 0.3s ease-in-out; text-align: right; font-size: large;')
        newitem_rate_div.string = str("{:.2f}".format(float(billitem[2])))
        
        newitem_qty_div = templatesoup.new_tag('div', style='margin: 3px; width: 7%; font-weight: bold;transition: all 0.3s ease-in-out; text-align: right; font-size: large;')
        newitem_qty_div.string = str(billitem[3])
        
        newitem_amount_div = templatesoup.new_tag('div', style='padding-right:3px; margin: 3px; width: 16%; font-weight: bold;transition: all 0.3s ease-in-out; text-align: right; font-size: large;')
        newitem_amount_div.string = str("{:.2f}".format(float(billitem[4])))

        newitemrow_div.append(newitem_slno_div)
        newitemrow_div.append(newitem_name_div)
        newitemrow_div.append(newitem_rate_div)
        newitemrow_div.append(newitem_qty_div)
        newitemrow_div.append(newitem_amount_div)

        billboxdiv.append(newitemrow_div)
    
    totallabeldiv = templatesoup.find(id="total_label")
    if totallabeldiv:
        totallabeldiv.string = str("{:.2f}".format(float(total)))

    if float(discountpercent_onbill) != 0:
        discountpercentlabeldiv = templatesoup.find(id='discountlabel')
        if discountpercentlabeldiv:
            discountpercentlabeldiv.string = str(discountpercent_onbill)
    else:
        discountlabel = templatesoup.find(id='discountlabellabel')
        discountlabel.string = ""

    if float(deliverycharges) != 0:
        deliverychargeslabeldiv = templatesoup.find(id='deliverycharge_label')
        if deliverychargeslabeldiv:
            deliverychargeslabeldiv.string = str(deliverycharges)
    else:
        deliverylabel = templatesoup.find(id='deliverylabel')
        deliverylabel.string = ""
    
    custcopytext = templatesoup.find(id='office_cust_copy_txt')
    if custcopytext:
        custcopytext.string = "(Customer Copy)"

    timestamplabel = templatesoup.find(id="timestamp")
    if timestamplabel:
        timestamplabel.string = str(datetime.datetime.now())

    with open(r'./temp/custcopytemp.html', 'w') as file:
        file.write(str(templatesoup))

    # print(templatesoup)
    pdfpath = r'./generatedbills/' + str(billno) + r'/' + "customercopybill_" + str(billno) + "_" + str(int(time.time())) + ".pdf"
    os.makedirs(os.path.dirname(pdfpath), exist_ok=True)

    htmlpath = r'./temp/custcopytemp.html'
    with open(htmlpath, 'r') as htmlfile:
        htmlcontent = htmlfile.read()
    print(pdfpath)
    asyncio.run(html_to_pdf(htmlcontent, pdfpath))
    os.system('\"'+os.path.abspath(pdfpath)+'\"')
    bring_pdf_to_front(pdfpath.split("/")[-1])
    # HTML(string=htmlcontent).write_pdf(pdfpath)

    # asyncio.get_event_loop().run_until_complete(generate_pdf_from_html(htmlcontent, pdfpath))

    # with open(pdfpath, 'wb') as pdffile:
    #     pisa_status = pisa.CreatePDF(htmlcontent, dest=pdffile)


    return


@eel.expose
def say_hello_py():
    print("Hello world")
    return "Hello from Python!"

@eel.expose
def getAllItemsList():
    global menudat_json
    retarray = []
    for key, item in menudat_json.items():
        retarray.append(str(key) + " " + str(item["itemname"]))
    # print(retarray)
    return retarray

@eel.expose
def menusearch(searchcrit):
    global menudat_json
    retarr = []
    searcharray = [value["itemname"].lower() for key, value in menudat_json.items()]
    for i in range(len(searcharray)):
        if searchcrit in searcharray[i]:
            retarr.append(str(i+1) + " " + menudat_json[str(i+1)]["itemname"])
    return retarr

@eel.expose
def getDefaultDets(itemid):
    global menudat_json
    retarr_item = [itemid, menudat_json[itemid]["itemname"], menudat_json[itemid]["itemrate"]]
    return retarr_item

@eel.expose
def getrandid():
    l1 = 'abcdefghijklmnopqrstuvwxyz0123456789'
    retval = ""
    for i in range(4):
        retval += random.choice(list(l1))
    return retval

@eel.expose
def getNewBillID():
    global conn
    cursor = conn.cursor()
    alldat = cursor.execute("SELECT MAX(billno) FROM billingdata;").fetchall()
    print("alldat: " ,alldat)
    # return "0000"
    if len(alldat) == 0 or alldat==None or alldat[0][0]==None:
        return "0001"
    else:
        # lastbill = int(alldat[-1][1])
        thisbill = int(alldat[0][0]) + 1
        if thisbill < 1000 and thisbill > 99:
            return "0" + str(thisbill)
        if thisbill < 100 and thisbill > 9:
            return "00" + str(thisbill)
        if thisbill < 10 and thisbill > 0:
            return "000" + str(thisbill)
        return thisbill

@eel.expose
def newBill(current_billno,
        current_customername,
        current_kotnums,
        current_roomnums,
        keylist,
        newbill_objectlist,
        discount_percent,
        delivery_charges,
        sumtotal,
        dateval):
    
    global conn

    print(current_billno)
    print(current_customername)
    print(current_kotnums)
    print(current_roomnums)
    print(keylist)
    print(newbill_objectlist)
    print(discount_percent)
    print(delivery_charges)
    print(sumtotal)

    conn.commit()
    conn.execute('DELETE FROM billingdata WHERE billno = ?', (current_billno,))
    try:
        if len(newbill_objectlist) > 0:
            for item in newbill_objectlist:
                params = ( str(current_billno) , str(dateval) , current_customername, str(current_roomnums) , str(current_kotnums) ,  str(item[1]) ,  str(item[5]) ,  str(item[2]) ,  str(item[3]) ,  str(item[4]) ,  discount_percent ,  delivery_charges ,  sumtotal ,)
                conn.execute('INSERT INTO billingdata VALUES (NULL, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', params)
                conn.commit()
        else:
            params = ( str(current_billno) , str(dateval) , current_customername, str(current_roomnums) , str(current_kotnums) , "" ,  "" ,  "" ,  "" ,  "" ,  discount_percent ,  delivery_charges ,  sumtotal ,)
            conn.execute('INSERT INTO billingdata VALUES (NULL, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', params)
            conn.commit()

    except Exception as e:
        print(e)
        conn.rollback()
        conn.commit()
    return

@eel.expose
def prevBillNo(currentbillno):
    if currentbillno == "0000":
        return "0000"
    billno_int = int(currentbillno)
    billno_int_prev = billno_int - 1
    if billno_int_prev < 1000 and billno_int_prev > 99:
        return "0" + str(billno_int_prev)
    if billno_int_prev < 100 and billno_int_prev > 9:
        return "00" + str(billno_int_prev)
    if billno_int_prev < 10 and billno_int_prev >= 0:
        return "000" + str(billno_int_prev)
    return billno_int_prev
    
@eel.expose
def nextBillNo(currentbillno):
    if currentbillno == "0000":
        return "0001"
    billno_int = int(currentbillno)
    billno_int_next = billno_int + 1
    if billno_int_next < 1000 and billno_int_next > 99:
        return "0" + str(billno_int_next)
    if billno_int_next < 100 and billno_int_next > 9:
        return "00" + str(billno_int_next)
    if billno_int_next < 10 and billno_int_next > 0:
        return "000" + str(billno_int_next)
    return billno_int_next
    


@eel.expose
def does_bill_exist(billno):
    retval = "not_exist"
    cursor = conn.cursor()
    billdat = cursor.execute("SELECT * FROM billingdata WHERE billno=?", (billno,)).fetchall()
    if len(billdat) > 0:
        return "exists"
    return retval

@eel.expose
def searchbills(criteria, field):
    print("searchbills: " + criteria + " " + field)
    resdat = []
    if criteria.strip() == "":
        resdat = conn.cursor().execute("SELECT DISTINCT billno, customerName FROM billingdata").fetchall()
    else:
        if field == "date":
            resdat = conn.cursor().execute("SELECT DISTINCT billno, billingdate FROM billingdata WHERE billingdate LIKE ?", ('%'+criteria+'%',)).fetchall()
        if field == "cname":
            resdat = conn.cursor().execute("SELECT DISTINCT billno, customerName FROM billingdata WHERE customerName LIKE ?", ('%'+criteria+'%',)).fetchall()
        if field == "kotnum":
            resdat = conn.cursor().execute("SELECT DISTINCT billno, kot_nums FROM billingdata WHERE kot_nums LIKE ?", ('%'+criteria+'%',)).fetchall()
    # print(resdat)
    resdat1 = [list(item) for item in resdat]
    # print(resdat1)
    return resdat1

@eel.expose
def fetchBillDataById(billno):

    cursor = conn.cursor()
    billrows = cursor.execute("SELECT * FROM billingdata WHERE billno=?", (billno,)).fetchall()
    if len(billrows) > 0:
        bill_no = billrows[0][1]
        billing_date = billrows[0][2]
        billed_customername = billrows[0][3]
        billing_roomnums = ast.literal_eval(billrows[0][4])
        billing_kotnums = ast.literal_eval(billrows[0][5])
        discountonbill = billrows[0][11]
        deliverychargeonbill = billrows[0][12]
        billing_sumtotal = billrows[0][13]
        items_arr = []
        for itemdets in billrows:
            items_arr.append([itemdets[6], itemdets[7], itemdets[8], itemdets[9], itemdets[10]])
        # print(items_arr)
        retarray = [bill_no,
                    billing_date,
                    billed_customername,
                    billing_roomnums,
                    billing_kotnums,
                    discountonbill,
                    deliverychargeonbill,
                    billing_sumtotal,
                    items_arr]
        return retarray

@eel.expose
def getTodate():
    datelst = str(datetime.datetime.today()).split(" ")[0].split("-")
    todate = datelst[2] + "/" + datelst[1] + "/" + datelst[0]
    return todate

eel.start('index.html', size=(1150, 600))
