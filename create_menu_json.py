import json
import pandas
import pprint

menudat_xlsx_file = r'./dat/menu card.xlsx'

menu_df = pandas.read_excel(menudat_xlsx_file)

print(menu_df.shape)
print(menu_df.columns)

menulist = menu_df.values.tolist()
print(menulist)

# json_dat = menu_df.values.tolist()
json_dat = {}
for item in menulist:
    print(item)
    itemdat = {"itemname":item[1],
               "itemrate":item[2]}
    json_dat[item[0]] = itemdat


print(json_dat)
with open(r'./dat/menujson.json', "w") as menujsonfile:
    json.dump(json_dat, menujsonfile)
