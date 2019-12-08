import webbrowser, os, sys
from socket import *
root = os.getcwd()
s = socket(AF_INET, SOCK_DGRAM)
port = sys.argv[1]
try:
	s.connect(('8.8.8.8', 8001))
	IP = s.getsockname()[0]
except:
	IP = '127.0.0.1'
s.close()
vice_url = "http://" + 	IP + ":" + port + root
def starttab(url = (vice_url)):
    webbrowser.open_new_tab(url)


starttab(vice_url + "/song.mp3")
starttab(vice_url + "/video.mp4")
starttab(vice_url + "/form.html")
starttab(vice_url + "/help.txt")
starttab(vice_url + "/1.jpeg")
starttab(vice_url + "/hci.pdf")
starttab(vice_url + "/snapshot")
starttab(vice_url + "/website/home.html")
