# UIC Timetable vote tools  
## Usage
1. Clone 
2. Open main.py  
3. Modify ADDRESS, DONAME, APP_SECRET_KEY  
Flask will listen on ADDRESS[0] and port ADDRESS[1]  
DONAME will be shown on page.html  
For example: if your DOMAIN is example.com  
Then the hint on the page is  
"This page URL is http://example.com:8080/page/6563 You can share this link with your friend and let them vote!"  
APP_SECRETY_KEY is used to encrypt flask session