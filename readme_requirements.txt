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

billing_dbms.db structure

