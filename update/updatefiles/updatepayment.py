import eel
import ast
import sqlite3
import os
import sys
import argparse
import datetime
import pprint
import time
import xlsxwriter

# parser = argparse.ArgumentParser(description="opening arguments")

# parser.add_argument('--billno', default="0001")

# args = parser.parse_args()

currentpayment_billid = "0001"

print(currentpayment_billid)

eel.init("paymentinterface")

conn = sqlite3.connect(r'./sqlite3/billing_dbms.db')

def get_date_x_days_before(date_str, x):
    """
    Computes the date that is x days before the given date.

    Parameters:
        date_str (str): The date in the format 'dd/mm/yyyy'.
        x (int): The number of days before the given date.

    Returns:
        str: The date in the format 'dd/mm/yyyy' that is x days before the given date.
    """
    # Convert the string date to a datetime object
    date_obj = datetime.datetime.strptime(date_str, "%d/%m/%Y")

    # Subtract x days from the date
    new_date_obj = date_obj - datetime.timedelta(days=x)

    # Convert the new date back to string format
    new_date_str = new_date_obj.strftime("%d/%m/%Y")

    return new_date_str

def date_string_to_timestamp(date_str):
    """
    Converts a date string in the format 'dd/mm/yyyy' to a Unix timestamp.

    Parameters:
        date_str (str): The date string in 'dd/mm/yyyy' format.

    Returns:
        int: The Unix timestamp corresponding to the given date.
    """
    # Convert the date string to a datetime object
    date_obj = datetime.datetime.strptime(date_str, "%d/%m/%Y")

    # Convert the datetime object to a Unix timestamp
    unix_timestamp = int(date_obj.timestamp())

    return unix_timestamp

@eel.expose
def gensummary_lastndays(n):
    todate = getTodate()
    initdate = get_date_x_days_before(todate, int(n))

    starttimestamp = date_string_to_timestamp(initdate)
    endtimestamp = date_string_to_timestamp(todate)

    global conn

    billnos_inrange = conn.cursor().execute("SELECT billno FROM paymentdata WHERE timestamp BETWEEN ? AND ?", (starttimestamp, endtimestamp, )).fetchall()
    if len(billnos_inrange) > 1:
        billnolist_values = set([i[0] for i in billnos_inrange])
        print(billnolist_values)
        gensummary = gensummary_bno(None, None, billnolist=billnolist_values)
        return gensummary

    return "Insufficient Records to create Summary in given Range"

@eel.expose
def gensummary_bno(startingbno, endingbno, billnolist=None):
    try:
        global conn
        restaurantamount = 0
        resortamount = 0        # program to calculate this next
        SumTotalBilled = 0
        summary_records_csv = [["Dates", "Bill Number", "Customer Name", "Room No.", "Total", "Paid", "Due", "Cash", "UPI", "Card", "Bank Transfer"],
                                ["","","","","","","","","","",""]
                            ]
        if billnolist == None:
            for i in range(int(startingbno), int(endingbno) + 1):
                billno_id = getBillNoFromInt(i)
                paymentrecords = conn.cursor().execute("SELECT * FROM paymentdata WHERE billno = ?", (billno_id, )).fetchall()
                latestrecord = None
                if len(paymentrecords) > 0:
                    latestrecord = paymentrecords[-1]
                # if latestrecord != None:
                    sqljson = ast.literal_eval(latestrecord[2])
                    
                    billingdat = conn.cursor().execute("SELECT * FROM billingdata WHERE billno = ?", (billno_id, )).fetchall()
                    
                    # dates, billno, custname, roomnums, total, paid, due, cash, upi, card, bt

                    # print("###")
                    # print(type(sqljson))
                    # print(sqljson)
                    # print(type(billno))
                    # print(billno)
                    # print(type(roomnums))
                    # print(roomnums)
                    
                    dates = []
                    for paymentrecord_json in sqljson[0]:
                        date = paymentrecord_json[1]
                        if date not in dates:
                            dates.append(date)

                    datestring = ",".join(dates)
                    billno = str(latestrecord[1])
                    
                    roomnums = ""
                    custname = "UNKNOWN"
                    total = str(latestrecord[-1])
                    totalamount = str(sqljson[2])
                    if len(billingdat) > 0:
                        roomnums = billingdat[0][4]
                        custname = billingdat[0][3]
                    
                        totalamount = str(billingdat[0][-1])

                    dueamount = str(sqljson[1])
                    paidamount = str(int(totalamount) - int(dueamount))
                    
                    cashpaid = 0
                    upipaid = 0
                    cardpaid = 0
                    btpaid = 0
                    for prec in sqljson[0]:
                        if prec[0] == "cashmethod":
                            cashpaid += float("{:.2f}".format(float(prec[2])))
                        if prec[0] == "upimethod":
                            upipaid += float("{:.2f}".format(float(prec[2])))
                        if prec[0] == "cardmethod":
                            cardpaid += float("{:.2f}".format(float(prec[2])))
                        if prec[0] == "btransfermethod":
                            btpaid += float("{:.2f}".format(float(prec[2])))
                    if "t" in str(roomnums) or "T" in str(roomnums) or "RP" in str(roomnums) or "rp" in str(roomnums):
                        restaurantamount += float("{:.2f}".format(float(totalamount)))
                    else:
                        resortamount += float("{:.2f}".format(float(totalamount)))
                    SumTotalBilled += float("{:.2f}".format(float(totalamount)))
                    prec_summary = [datestring,
                                    billno,
                                    custname, 
                                    roomnums, 
                                    totalamount, 
                                    paidamount, 
                                    dueamount,
                                    str(cashpaid),
                                    str(upipaid),
                                    str(cardpaid),
                                    str(btpaid)
                                ]

                    summary_records_csv.append(prec_summary)
            desktoppath = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
            workbook = xlsxwriter.Workbook(desktoppath + '\\paymentsummary'+str(int(time.time())) + ".xlsx")
            worksheet = workbook.add_worksheet("summarysheet")
            # cell_format = workbook.add_format({'align': 'center', 'valign': 'vcenter'})
            # worksheet.set_column("E:K", None, cell_format)
            currency_format = workbook.add_format({'num_format': '#,##0.00'})
            row = 0
            col = 0
            for dates, bno, cname, rns, tamount, pamount, damount, cp, up, cdp, btp in (summary_records_csv):
                worksheet.write(row, col, dates)
                worksheet.write(row, col+1, bno)
                worksheet.write(row, col+2, cname)
                worksheet.write(row, col+3, rns)
                try:
                    worksheet.write(row, col+4, float("{:.2f}".format(float(tamount))), currency_format)
                except:
                    worksheet.write(row, col+4, tamount, currency_format)
                worksheet.write(row, col+5, pamount)
                worksheet.write(row, col+6, damount)
                worksheet.write(row, col+7, cp)
                worksheet.write(row, col+8, up)
                worksheet.write(row, col+9, cdp)
                worksheet.write(row, col+10, btp)
                row += 1
            row += 2
            col = 3
            worksheet.write(row, col, "Restaurant Total")
            worksheet.write(row, col + 1, restaurantamount, currency_format)
            row += 1
            worksheet.write(row, col, "Resort Total")
            worksheet.write(row, col + 1, resortamount)
            row += 1
            worksheet.write(row, col, "Restaurant + Resort")
            worksheet.write(row, col + 1, resortamount+restaurantamount, currency_format)
            row += 1
            worksheet.write(row, col, "Sum Total Billed")
            worksheet.write(row, col + 1, SumTotalBilled, currency_format)
            workbook.close()
            return "Summary Created Successfully!!!"
        else:
            for billno_id in billnolist:
                # billno_id = getBillNoFromInt(i)
                paymentrecords = conn.cursor().execute("SELECT * FROM paymentdata WHERE billno = ?", (billno_id, )).fetchall()
                latestrecord = None
                if len(paymentrecords) > 0:
                    latestrecord = paymentrecords[-1]
                # if latestrecord != None:
                    sqljson = ast.literal_eval(latestrecord[2])
                    
                    billingdat = conn.cursor().execute("SELECT * FROM billingdata WHERE billno = ?", (billno_id, )).fetchall()
                    
                    # dates, billno, custname, roomnums, total, paid, due, cash, upi, card, bt

                    # print("###")
                    # print(type(sqljson))
                    # print(sqljson)
                    # print(type(billno))
                    # print(billno)
                    # print(type(roomnums))
                    # print(roomnums)
                    
                    dates = []
                    for paymentrecord_json in sqljson[0]:
                        date = paymentrecord_json[1]
                        if date not in dates:
                            dates.append(date)

                    datestring = ",".join(dates)
                    billno = str(latestrecord[1])
                    
                    roomnums = ""
                    custname = "UNKNOWN"
                    total = str(latestrecord[-1])
                    totalamount = str(sqljson[2])
                    if len(billingdat) > 0:
                        roomnums = billingdat[0][4]
                        custname = billingdat[0][3]
                    
                        totalamount = str(billingdat[0][-1])

                    dueamount = str(sqljson[1])
                    paidamount = str(int(totalamount) - int(dueamount))
                    
                    cashpaid = 0
                    upipaid = 0
                    cardpaid = 0
                    btpaid = 0
                    for prec in sqljson[0]:
                        if prec[0] == "cashmethod":
                            cashpaid += float("{:.2f}".format(float(prec[2])))
                        if prec[0] == "upimethod":
                            upipaid += float("{:.2f}".format(float(prec[2])))
                        if prec[0] == "cardmethod":
                            cardpaid += float("{:.2f}".format(float(prec[2])))
                        if prec[0] == "btransfermethod":
                            btpaid += float("{:.2f}".format(float(prec[2])))
                    if "t" in str(roomnums) or "T" in str(roomnums) or "RP" in str(roomnums) or "rp" in str(roomnums):
                        restaurantamount += float("{:.2f}".format(float(totalamount)))
                    else:
                        resortamount += float("{:.2f}".format(float(totalamount)))
                    SumTotalBilled += float("{:.2f}".format(float(totalamount)))
                    prec_summary = [datestring,
                                    billno,
                                    custname, 
                                    roomnums, 
                                    totalamount, 
                                    paidamount, 
                                    dueamount,
                                    str(cashpaid),
                                    str(upipaid),
                                    str(cardpaid),
                                    str(btpaid)
                                ]

                    summary_records_csv.append(prec_summary)
            desktoppath = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
            workbook = xlsxwriter.Workbook(desktoppath + '\\paymentsummary'+str(int(time.time())) + ".xlsx")
            worksheet = workbook.add_worksheet("summarysheet")
            # cell_format = workbook.add_format({'align': 'center', 'valign': 'vcenter'})
            # worksheet.set_column("E:K", None, cell_format)
            currency_format = workbook.add_format({'num_format': '#,##0.00'})
            row = 0
            col = 0
            for dates, bno, cname, rns, tamount, pamount, damount, cp, up, cdp, btp in (summary_records_csv):
                worksheet.write(row, col, dates)
                worksheet.write(row, col+1, bno)
                worksheet.write(row, col+2, cname)
                worksheet.write(row, col+3, rns)
                try:
                    worksheet.write(row, col+4, float("{:.2f}".format(float(tamount))), currency_format)
                except:
                    worksheet.write(row, col+4, tamount, currency_format)
                worksheet.write(row, col+5, pamount)
                worksheet.write(row, col+6, damount)
                worksheet.write(row, col+7, cp)
                worksheet.write(row, col+8, up)
                worksheet.write(row, col+9, cdp)
                worksheet.write(row, col+10, btp)
                row += 1
            row += 2
            col = 3
            worksheet.write(row, col, "Restaurant Total")
            worksheet.write(row, col + 1, restaurantamount, currency_format)
            row += 1
            worksheet.write(row, col, "Resort Total")
            worksheet.write(row, col + 1, resortamount)
            row += 1
            worksheet.write(row, col, "Restaurant + Resort")
            worksheet.write(row, col + 1, resortamount+restaurantamount, currency_format)
            row += 1
            worksheet.write(row, col, "Sum Total Billed")
            worksheet.write(row, col + 1, SumTotalBilled, currency_format)
            workbook.close()
            return "Summary Created Successfully!!!"

        # pprint.pprint(summary_records_csv)
    except Exception as e:
        print(e)
        return "Failed to create summary"

@eel.expose
def getFirstPaymentLoadBillNo():
    return "0001"

@eel.expose
def updatePayment_db(paymenthashmap, paymentbillno, billedamount, dueamount):
    # print("\n" + str(paymentbillno))
    # pprint.pprint(paymenthashmap)

    global conn

    paymentjsontext = f"[" + str(paymenthashmap) + f", {dueamount}, {billedamount}]"
    print(paymentjsontext)
    try:
        conn.execute("INSERT INTO paymentdata VALUES (NULL, ?, ?, ?)", (str(paymentbillno), paymentjsontext, str(int(time.time()))))
        conn.commit()
        return "Database Successfully Updated"
    except:
        return "Failed to update database !!!"

def getBillNoFromInt(intbillno):
    if intbillno < 1000 and intbillno > 99:
        return "0" + str(intbillno)
    if intbillno < 100 and intbillno > 9:
        return "00" + str(intbillno)
    if intbillno < 10 and intbillno >= 0:
        return "000" + str(intbillno)
    return str(intbillno)

@eel.expose
def prevBillNo(currentbillno):
    if currentbillno == "0001":
        return "0001"
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
    if currentbillno == "0001":
        return "0002"
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
def does_bill_exist_payment(billno):
    global conn

    retval = "not_exist"
    cursor = conn.cursor()
    billdat = cursor.execute("SELECT * FROM billingdata WHERE billno=?", (str(billno),)).fetchall()
    if len(billdat) > 0:
        return "exists"
    return retval

@eel.expose
def getTodate():
    datelst = str(datetime.datetime.today()).split(" ")[0].split("-")
    todate = datelst[2] + "/" + datelst[1] + "/" + datelst[0]
    return todate

@eel.expose
def getPaymentStatusData(paymentbillno):
    global conn
    sqlpaymentdata = conn.cursor().execute("SELECT * FROM paymentdata WHERE billno = ?", (str(paymentbillno), )).fetchall()
    if not len(sqlpaymentdata) > 0:
        billdat = conn.cursor().execute("SELECT * FROM billingdata WHERE billno=?", (paymentbillno,)).fetchall()
        if len(billdat) > 0:
            billedamnt = billdat[0][13]
            newjsontext = f"[[], {billedamnt}, {billedamnt}]"
            conn.execute("INSERT INTO paymentdata VALUES (NULL, ?, ?, ?)", (str(paymentbillno), newjsontext, str(int(time.time())), )) # [ 
            conn.commit()     
            sqlpaymentdata = conn.cursor().execute("SELECT * FROM paymentdata WHERE billno = ?", (str(paymentbillno), )).fetchall()
        else:
            return "Billing record does not exist for this bill number !!!"
    latestrecord = ast.literal_eval(sqlpaymentdata[-1][2])
    commentlist = []
    paymentmethodlist = []
    datelist = []
    amountpaidlist = []

    # return values
    for payment in latestrecord[0]:
        paymentmethodlist.append(payment[0])
        datelist.append(payment[1])
        amountpaidlist.append(payment[2])
        commentlist.append(payment[3])
    dueamount = latestrecord[1]
    billedamount = latestrecord[2]
    timestamp = sqlpaymentdata[-1][3] 

    retcustname = ""
    custname = conn.cursor().execute("SELECT customerName FROM billingdata WHERE billno = ?", (str(paymentbillno), )).fetchall()
    if len(custname) > 0:
        retcustname = custname[0]
    else:
        retcustname = "UNKNOWN"

    return paymentmethodlist, datelist, amountpaidlist, commentlist, dueamount, billedamount, timestamp, retcustname

eel.start("index.html", size=(650,500), port=8001)