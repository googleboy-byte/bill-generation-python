import sqlite3
import json
import os
import shutil
import pprint
import time

conn = sqlite3.connect(r'../sqlite3/billing_dbms.db')


configdat = None
with open("config.json", "r") as configfile:
	configdat = json.load(configfile)

updatepaths = [i.replace("root/", "../") for i in configdat["updatedfiles"].values()]
addedpaths = [i.replace("root/", "../") for i in configdat["addedfiles"].values()]

os.system("pip install xlsxwriter")

pprint.pprint(updatepaths)
pprint.pprint(addedpaths)

def updatesqltable():
	global conn
	print("[+] Updating SQLITE DB...\n")
	paymentdata_createtable = '''CREATE TABLE "paymentdata" (
		"id"	INTEGER NOT NULL UNIQUE,
		"billno"	TEXT,
		"paymentjson"	TEXT,
		"timestamp"	TEXT,
		PRIMARY KEY("id" AUTOINCREMENT)
	);'''

	ret2 = conn.cursor().execute("SELECT name FROM sqlite_master WHERE type='table' AND name='paymentdata'").fetchall()
	if len(ret2) == 0:
		conn.cursor().execute(paymentdata_createtable)
		conn.commit()
		print("[+] Successfully modified sqlite db struct...")
	
	return


def updatefiles():
	global updatepaths
	print("[+] Copying updated files...\n")
	for path in updatepaths:
		print("[.] Copying Path:", path)
		shutil.copy2(path.replace("../", "./updatefiles/"), path)
		time.sleep(0.1)
	return

def addfiles():
	global addedpaths
	print("[+] Copying added files...\n")
	for path_added in addedpaths:
		print("[.] Checking Path:", os.path.dirname(path_added))
		os.makedirs(os.path.dirname(path_added), exist_ok=True)
		time.sleep(0.1)
		print("[.] Copying Path:", path_added)
		shutil.copy2(path_added.replace("../", "./updatefiles/"), path_added)
		time.sleep(0.1)
	return

print()
updatesqltable()
updatefiles()
addfiles()
print("\n[+] Update Complete!!!")
