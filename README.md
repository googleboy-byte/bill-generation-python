# bill-generation-python
GUI based billing software created with python and sqlite as backend and html/js as web based frontend, run on localhost, using eel framework to connect frontend to backend

![Screenshot (207)](https://github.com/user-attachments/assets/2b86df0f-05a6-41a5-9287-67ea59a81beb)

![image](https://github.com/user-attachments/assets/4f2ec0c1-de0a-4b43-a597-1cba96deb0a3)


To change bill output format, edit billtemplate.html under ./template_html/ folder. Python file main.py references billtemplate.html when generating new bill. It sets bill values using bs4 Beautiful Soup by identifying the specific value fields using the div id. So change that accordingly in both main.py code and billtemplate.html code. Taxation code has not been added yet. But, extra charge can be added as a new item or as a negative discount of the sumtotal. Running main.py should start the program. Tested on windows 10 and windows 11. Check below dependencies before running program.

py libs (dependencies)

-eel
-json
-random
-datetime
-sqite3
-ast
-bs4
-os
-time
-requests
-asyncio
-playwright
-shutil
-pandas
-openpyxl

other dependencies

-gtk3+

folder structure

./
	dat/	{mustpresent}
		menu_card.xlsx	{mustpresent}
		menujson.json 	{mustpresent_generatedby_../../create_menu_json.py}

	generatedbills/	{mustpresent}
		{billno}/	{maypresent}
			customercopybill_{billno}_{epochtimestamp}.pdf	{mustpresent_generatedby_../../main.py}
			officecopybill_{billno}_{epochtimestamp}.pdf	{mustpresent_generatedby_../../main.py}
		
	interface/	{mustpresent}
		index.html	{mustpresent}
		script.js	{mustpresent}
		styles.css	{mustpresent}

	sqlite3/	{mustpresent}
		billing_dbms.db	{mustpresent}

	temp/	{mustpresent}
		custcopytemp.html	{maypresent_generatedby_../main.py}
		officecopytemp.html	{maypresent_generatedby_../main.py}

	template_html/	{mustpresent}
		billtemplate.html	{mustpresent}

	create_menu_json.py	{mustpresent}
	main.py			{mustpresent}
	readme_requirements.txt	{mustpresent}
