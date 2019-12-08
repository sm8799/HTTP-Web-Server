import os

''' data size to receive from client'''
SIZE = 8192

'''this initiation helps server to identify current working directory'''
ROOT = os.getcwd()

''' 
browser demands favicon.ico file to show the icon in the tab of its window 
we define its path here
'''
favicon = '/favicon.ico'
FAVICON = ROOT + favicon

'''
supported version by the server. 
The implementation of the version is the choice of the server designer
''' 
RUNNING_VERSION = '1.1'

'''
Thread requests handled by the server at one time
'''
MAX_REQUESTS = 100

'''
Maximum Url length supported by the server 
at the instance when new connection arrives 
'''
MAX_URL = 150

'''
log file to handle misachievious actions
'''
LOG = ROOT + '/server.log'
w = open(LOG, "a")
w.close()
'''
this file is made only for project execution and not as the part of the server
html file gives response to the client once they use get or post method using 
query or entity data respectively
'''
WORKFILE = ROOT + '/workfile.html'

'''
this snippet makes workfile
'''
w = open(WORKFILE, "w")
d = '<html><head><title>Thank for response</title></head><body><h1>Response  Saved</h1></body></html>'
w.write(d)
w.close()

'''
csv file is the used to store the data entered by user
'''

CSVFILE = ROOT + '/action_page.csv'
w = open(CSVFILE, "a")
w.close()
'''
this folder contains all the files which are being deleted by the requests
processed by the server
'''
DELETE = ROOT + '/delete'

'''
this snippet gives a try to make delete folder 
to save unwanted deletions from the system
'''
try:
	os.mkdir(DELETE)
except:
	pass

'''
username and password for approval of delete request method
'''
USERNAME = 'MSD'
PASSWORD = 'mahi7781'

'''
cookie max age 
'''
COOKIE = 'Set-Cookie: id='
MAXAGE = '; max-age=3600'
