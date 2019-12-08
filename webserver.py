from socket import *         # to implement webserver
from datetime import *		 # to implement conditional get
import os					 # to use basic facilities of checking path,file, directory
import time					 # to implement conditional get
import random				 # to implement randomness so that some of the status codes get implemented
import threading			 # to handle requests coming to server
from urllib.parse import *	 # for parsing URL/URI
from _thread import *
import shutil				 # to implement delete method
import mimetypes			 # for getting extensions as well as content types
import csv					 # used in get and post method to insert the data into file
import base64				 # used for decoding autherization header in delete method
import sys					 # for arguements, exits
import logging				 # for logging
serversocket = socket(AF_INET, SOCK_STREAM)
s = socket(AF_INET, SOCK_DGRAM)
from config import *

logging.basicConfig(filename = LOG, level = logging.INFO, format = '%(asctime)s:%(filename)s:%(message)s')

#dictionary to convert extensions into content types
file_extension = {'.html':'text/html', '.txt':'text/plain', '.png':'image/png', '.gif': 'image/gif', '.jpg':'image/jpg', '.ico': 'image/x-icon', '.php':'application/x-www-form-urlencoded', '': 'text/plain', '.jpeg':'image/webp', '.pdf': 'application/pdf', '.js': 'application/javascript', '.css': 'text/css', '.mp3' : 'audio/mpeg'}

#dictionary to convert content types into extensions
file_type = {'text/html': '.html','text/plain': '.txt', 'image/png': '.png', 'image/gif': '.gif', 'image/jpg': '.jpg','image/x-icon':'.ico', 'image/webp': '.jpeg', 'application/x-www-form-urlencoded':'.php', 'image/jpeg': '.jpeg', 'application/pdf': '.pdf', 'audio/mpeg': '.mp3', 'video/mp4': '.mp4'}

#dictionary to convert month to its decimal
month = { 'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6, 'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12 }

c_get = False    			 # to check the conditional get method
conn = True					 # to receive requests continuously in client's thread
lthread = []				 # list to maintain threads
ip = '0.0.0.0'
SERVER = True				 # to stop server
MAIN = True					 # to close server
scode = 0					 # status code
IDENTITY = 0				 # cookie value

# function to fetch last modified date of the resource
def last_modified(element):
	l = time.ctime(os.path.getmtime(element)).split(' ')
	for i in l:
		if len(i) == 0:
			l.remove(i)
	l[0] = l[0] + ','
	string = (' ').join(l)
	string = 'Last-Modified: ' + string
	return string

#function to check if the resource has been modified or not since the date in HTTP request 
def if_modify(state, element):
	global c_get
	day = state.split(' ')
	if len(day) == 5:
		global month
		m = month[day[1]]
		date = int(day[2])
		t = day[3].split(':')
		t[0], t[1], t[2] = int(t[0]), int(t[1]), int(t[2])
		y = int(day[4])
		ti = datetime(y, m, date, t[0], t[1], t[2])
		hsec = int(time.mktime(ti.timetuple()))
		fsec = int(os.path.getmtime(element))
		if hsec == fsec:
			c_get = True
		elif hsec < fsec:
			c_get = False

#function to return current date
def date():
	l = time.ctime().split(' ')
	l[0] = l[0] + ','
	string = (' ').join(l)
	string = 'Date: ' + string
	return string

#function to give response if server is busy
def status(connectionsocket, code):
	global ip, lthread, scode
	scode = code
	display = []
	if code == 500:
		display.append('HTTP/1.1 500 Internal Server Error')
	elif code == 503:
		display.append('HTTP/1.1 503 Server Unavailable')
	elif code == 505:
		display.append('HTTP/1.1 505 HTTP Version Not Supported')
	elif code == 403:
		display.append('HTTP/1.1 403 Forbidden')
	elif code == 404:
		display.append('HTTP/1.1 404 Not Found')
	elif code == 414:
		display.append('HTTP/1.1 414 Request-URI Too Long')
	elif code == 415:
		display.append('HTTP/1.1 415 Unsupported Media Type')
	display.append('Server: ' + ip)
	display.append(date())
	display.append('\r\n')
	if code == 505:
		display.append('Supported Version - HTTP/1.1 \n Rest Unsupported')
	encoded = '\r\n'.join(display).encode()
	connectionsocket.send(encoded)
	logging.info('	{}	{}\n'.format(connectionsocket, scode))
	try:
		lthread.remove(connectionsocket)
		connectionsocket.close()
	except:
		pass
	server()

#function for conditional get implementation
def status_304(connectionsocket, element):
	global ip
	scode = 304
	display = []
	display.append('HTTP/1.1 304 Not Modified')
	display.append(date())
	display.append(last_modified(element))
	display.append('Server: ' + ip)
	display.append('\r\n')
	encoded = '\r\n'.join(display).encode()
	connectionsocket.send(encoded)

#function to resolve url in request message
def resolve(element):
	u = urlparse(element)
	element = unquote(u.path)
	if element == '/':
		element = os.getcwd()
	query = parse_qs(u.query)
	return (element, query)

#function to implement put method
def method_put(connectionsocket, addr, ent_body, filedata, element, switcher, f_flag):
	global scode
	display = []
	isfile = os.path.isfile(element)
	isdir = os.path.isdir(element)
	try:
		length = int(switcher['Content-Length'])
	except KeyError:
		status(connectionsocket, 411)
	q = int(length // SIZE)
	r = length % SIZE
	try:
		filedata = filedata + ent_body
	except TypeError:
		ent_body = ent_body.encode()
		filedata = filedata + ent_body
	i = len(ent_body)
	size = length - i
	while size > 0:
		ent_body = connectionsocket.recv(SIZE)
		try:
			filedata = filedata + ent_body
		except TypeError:
			ent_body = ent_body.encode()
			filedata = filedata + ent_body
		size = size - len(ent_body)
	move_p, mode_f, r_201 = False, True, False
	isfile = os.path.isfile(element)
	isdir = os.path.isdir(element)
	l = len(element)
	limit = len(ROOT)
	if l >= limit:
		if isdir:
			if os.access(element, os.W_OK):
				pass
			else:
				status(connectionsocket, 403)
			move_p = True
			loc = ROOT + '/' + str(addr[1])
			try:
				loc = loc + file_type[switcher['Content-Type'].split(';')[0]]
			except:
				status(connectionsocket, 403)
			if f_flag == 0:	
				f = open(loc, "w")
				f.write(filedata.decode())
			else:
				f = open(loc, "wb")
				f.write(filedata)
			f.close()
		elif isfile:
			if os.access(element, os.W_OK):
				pass
			else:
				status(connectionsocket, 403)
			mode_f = True
			if f_flag == 0:	
				f = open(element, "w")
				f.write(filedata.decode())
			else:
				f = open(element, "wb")
				f.write(filedata)
			f.close()
		else:
			#r = random.randint(0,4)
			if ROOT in element:
				r_201 = True
				element = ROOT + '/' + str(addr[1])
				try:
					element = element + file_type[switcher['Content-Type'].split(';')[0]]
				except:
					status(connectionsocket, 403)
				if f_flag == 0:	
					f = open(element, "w")
					f.write(filedata.decode())
				else:
					f = open(element, "wb")
					f.write(filedata)
				f.close()
			else:
				mode_f = False
	else:
		move_p = True
		loc = ROOT + '/' + str(addr[1])
		try:
			loc = loc + file_type[switcher['Content-Type']]
		except:
			status(connectionsocket, 403)
		if f_flag == 0:	
			f = open(loc, "w")
		else:
			f = open(loc, "wb")
		f.write(filedata)
		f.close()
	if move_p:
		scode = 301
		display.append('HTTP/1.1 301 Moved Permanently')
		display.append('Location: ' + loc)
	elif mode_f:
		scode = 204
		display.append('HTTP/1.1 204 No Content')
		display.append('Content-Location: ' + element)
	elif r_201:
		scode = 201
		display.append('HTTP/1.1 201 Created')
		display.append('Content-Location: ' + element)
	elif not mode_f:
		scode = 501
		display.append('HTTP/1.1 501 Not Implemented')
	display.append('Connection: keep-alive')
	display.append('\r\n')
	return display

#function to implement trace method
def method_trace(request, connectionsocket, switcher):
	global scode
	scode = 200
	display = []
	display.append('HTTP/1.1 200 OK')
	display.append('Content-Type: message/http')
	display.append('via: HTTP/1.1 ' + ip + ':' + str(serverport))
	display.append('\r\n')
	display.append(request)
	encoded = '\r\n'.join(display).encode()
	connectionsocket.send(encoded)

#commented function to implement connect method 
def method_connect(connectionsocket):
	global ip, scode
	scode = 204
	display.append('HTTP/1.1 204 No Content')
	display.append('Server: ' + ip)
	display.append('Connection: keep-alive')
	display.append(date())
	display.append('\r\n')
	encoded = '\r\n'.join(display).encode()
	connectionsocket.send(encoded)
	
#function to implement post method 		
def method_post(ent_body, connectionsocket, switcher):
	global ip, scode
	display = []
	query = parse_qs(ent_body)
	element = CSVFILE
	if os.access(element, os.W_OK):
		pass
	else:
		status(connectionsocket, 403)
	fields = []
	row = []
	for d in query:
		fields.append(d)
		for i in query[d]:
			row.append(i)
	check = os.path.exists(element)
	if check:
		fi = open(element, "a")
		display.append('HTTP/1.1 200 OK')
		scode = 200
		csvwriter = csv.writer(fi)
		csvwriter.writerow(row)
	else:
		fi = open(element, "w")
		display.append('HTTP/1.1 201 Created')
		scode = 201
		display.append('Location: ' + element)
		csvwriter = csv.writer(fi)
		csvwriter.writerow(fields)
		csvwriter.writerow(row)
	fi.close()
	display.append('Server: ' + ip)
	display.append(date())
	f = open(WORKFILE, "rb")
	display.append('Content-Language: en-US,en')
	size = os.path.getsize(WORKFILE)
	string = 'Content-Length: ' + str(size)
	display.append('Content-Type: text/html')
	display.append(string)
	display.append(last_modified(element))
	display.append('\r\n')
	encoded = '\r\n'.join(display).encode()
	connectionsocket.send(encoded)
	connectionsocket.sendfile(f)

#function to implement delete method
def method_delete(element, connectionsocket, ent_body, switcher):
	global ip, scode
	display = []
	option_list = element.split('/')
	isfile = os.path.isfile(element)
	isdir = os.path.isdir(element)
	if 'Authorization' in switcher.keys():
		string = switcher['Authorization']
		string = string.split(' ')
		string = base64.decodebytes(string[1].encode()).decode()
		string = string.split(':')
		if string[0] == USERNAME and string[1] == PASSWORD:
			pass
		else:
			scode = 401
			display.append('HTTP/1.1 401 Unauthorized')
			display.append('WWW-Authenticate: Basic')
			display.append('\r\n')
			encoded = '\r\n'.join(display).encode()
			connectionsocket.send(encoded)
			return
	else:
		scode = 401
		display.append('HTTP/1.1 401 Unauthorized')
		display.append('WWW-Authenticate: Basic')
		display.append('\r\n')
		encoded = '\r\n'.join(display).encode()
		connectionsocket.send(encoded)
		return
	if len(ent_body) > 1 or 'delete' in option_list or isdir:
		scode = 405
		display.append('HTTP/1.1 405 Method Not Allowed')
		display.append('Allow: OPTIONS, GET, HEAD, POST, PUT')
	elif isfile:
		a = random.randint(0,1)
		if a == 0:
			scode = 200
			display.append('HTTP/1.1 200 OK')
		else:
			scode = 204
			display.append('HTTP/1.1 204 No Content')
		try:
			if (os.access(element, os.W_OK) and os.access(element, os.R_OK)):
				pass
			else:
				status(connectionsocket, 403)
			shutil.move(element, DELETE)
		except shutil.Error:
			os.remove(element)
	else:
		scode = 400
		display.append('HTTP/1.1 400 Bad Request')
	display.append('Server: ' + ip)
	display.append('Connection: keep-alive')
	display.append(date())
	display.append('\r\n')
	encoded = '\r\n'.join(display).encode()
	connectionsocket.send(encoded)

#function to implement option method
def method_option(element, connectionsocket, switcher):
	global ip, scode
	isfile = os.path.isfile(element)
	isdir = os.path.isdir(element)
	display = []
	scode = 204
	display.append('HTTP/1.1 204 No Content')
	display.append('Server: ' + ip)
	display.append(date())
	display.append('Connection: close')
	option_list = element.split('/')
	if '*' in option_list and len(option_list) <= 2:
		display.append('Allow: OPTIONS, GET, HEAD, POST, PUT, DELETE')
	elif isfile or isdir:
		if 'delete' in option_list:
			display.append('Allow: OPTIONS')
		elif isfile:
			if (os.access(element, os.W_OK) and os.access(element, os.R_OK)):
				pass
			else:
				status(connectionsocket, 403)
			display.append('Allow: OPTIONS, GET, HEAD, POST')
		elif isdir:
			if (os.access(element, os.W_OK) and os.access(element, os.R_OK)):
				pass
			else:
				status(connectionsocket, 403)
			display.append('Allow: OPTIONS, GET, HEAD, POST, PUT')
	else:
		display.append('Allow: OPTIONS')
	display.append('\r\n')
	encoded = '\r\n'.join(display).encode()
	connectionsocket.send(encoded)

#function to implement get and head method
def method_get_head(connectionsocket, element, switcher, query, method):
	global serversocket, file_extension, c_get, conn, ip, scode, IDENTITY
	isfile = os.path.isfile(element)
	isdir = os.path.isdir(element)
	display = []
	if isfile:
		if (os.access(element, os.W_OK) and os.access(element, os.R_OK)):
			pass
		else:
			status(connectionsocket, 403)
		display.append('HTTP/1.1 200 OK')
		scode = 200
		try:
			f = open(element, "rb")
			size = os.path.getsize(element)
			data = f.read(size)
		except:
			status(connectionsocket, 500)
	elif isdir:
		if (os.access(element, os.W_OK) and os.access(element, os.R_OK)):
			pass
		else:
			status(connectionsocket, 403)
		display.append('HTTP/1.1 200 OK')
		scode = 200
		dir_list = os.listdir(element)
		for i in dir_list:
			if i.startswith('.'):
				dir_list.remove(i)
	else:
		element = element.rstrip('/')
		isfile = os.path.isfile(element)
		isdir = os.path.isdir(element)
		if isfile:
			if (os.access(element, os.W_OK) and os.access(element, os.R_OK)):
				pass
			else:
				status(connectionsocket, 403)
			display.append('HTTP/1.1 200 OK')
			scode = 200
			try:
				f = open(element, "rb")
				size = os.path.getsize(element)
				data = f.read(size)
			except:
				status(connectionsocket, 500)
		elif isdir:
			if (os.access(element, os.W_OK) and os.access(element, os.R_OK)):
				pass
			else:
				status(connectionsocket, 403)
			display.append('HTTP/1.1 200 OK')
			scode = 200
			dir_list = os.listdir(element)
			for i in dir_list:
				if i.startswith('.'):
					dir_list.remove(i)
		else:	
			status(connectionsocket, 404)
	display.append(COOKIE + str(IDENTITY) + MAXAGE)
	IDENTITY += 1
	for state in switcher:
		if state == 'Host':
			pass
		elif state == 'User-Agent':
			if isfile:
				display.append('Server: ' + ip)
				display.append(date())
				display.append(last_modified(element))
			elif isdir:
				display.append('Server: ' + ip)
		elif state == 'Accept':
			if isdir:
				string = 'Content-Type: text/html'
				display.append(string)
			elif isfile:
				try:
					file_ext = os.path.splitext(element)
					if file_ext[1] in file_extension.keys():
						string = file_extension[file_ext[1]]
					else:
						string = 'text/plain'
					string = 'Content-Type: '+ string
					display.append(string)
				except:
					status(connectionsocket, 415)
		elif state == 'Accept-Language':
			if isfile:
				string = 'Content-Language: ' + switcher[state]
				display.append(string)
			elif isdir:
				string = 'Content-Language: ' + switcher[state]
				display.append(string)
		elif state == 'Accept-Encoding':
			if isfile:
				string = 'Content-Length: ' + str(size)
				display.append(string)
		elif state == 'Connection':
			if isfile:
				conn = 	True
				display.append('Connection: keep-alive')
			elif isdir:
				conn = False
				display.append('Connection: close')
		elif state == 'If-Modified-Since':
			if_modify(switcher[state], element)
		elif state == 'Cookie':
			IDENTITY -= 1 
			display.remove(COOKIE + str(IDENTITY) + MAXAGE)
		else:
			continue
	if isdir and method == 'GET':
		display.append('\r\n')
		display.append('<!DOCTYPE html>')
		display.append('<html>\n<head>')
		display.append('<title>Directory listing</title>')
		display.append('<meta http-equiv="Content-type" content="text/html;charset=UTF-8" /></head>')
		display.append('<body><h1>Directory listing..</h1><ul>')
		for line in dir_list:
			if element == '/':
				link = 'http://' + ip + ':' + str(serverport) + element + line
				l = '<li><a href ="'+link+'">'+line+'</a></li>'
				display.append(l)
			else:
				link = 'http://' + ip + ':' + str(serverport) + element + '/'+ line
				l = '<li><a href ="'+link+'">'+line+'</a></li>'
				display.append(l)
		display.append('</ul></body></html>')
		encoded = '\r\n'.join(display).encode()
		connectionsocket.send(encoded)
		connectionsocket.close()
	elif len(query) > 0 and not isdir and not isfile:
		display = []
		element = CSVFILE
		fields = []
		row = []
		for d in query:
			fields.append(d)
			for i in query[d]:
				row.append(i)
		check = os.path.exists(element)
		if check:
			fi = open(element, "a")
			display.append('HTTP/1.1 200 OK')
			scode = 200
			csvwriter = csv.writer(fi)
			csvwriter.writerow(row)
		else:
			fi = open(element, "w")
			display.append('HTTP/1.1 201 Created')
			scode = 201
			display.append('Location: ' + element)
			csvwriter = csv.writer(fi)
			csvwriter.writerow(fields)
			csvwriter.writerow(row)
		fi.close()
		display.append('Server: ' + ip)
		display.append(date())
		f = open(WORKFILE, "rb")
		display.append('Content-Language: en-US,en')
		size = os.path.getsize(WORKFILE)
		string = 'Content-Length: ' + str(size)
		display.append('Content-Type: text/html')
		display.append(string)
		display.append(last_modified(element))
		display.append('\r\n')
		encoded = '\r\n'.join(display).encode()
		connectionsocket.send(encoded)
		connectionsocket.sendfile(f)
	elif isfile:
		display.append('\r\n')
		if c_get == False and method == 'GET':
			encoded = '\r\n'.join(display).encode()
			connectionsocket.send(encoded)
			connectionsocket.sendfile(f)
		elif c_get == False and method == 'HEAD':
			encoded = '\r\n'.join(display).encode()
			connectionsocket.send(encoded)
		elif c_get == True and (method == 'GET' or method == 'HEAD'):
			status_304(connectionsocket, element)
	else:
		status(connectionsocket, 400)
#function which operate on top of the methods i.e bridge between response and requests
def clientfun(connectionsocket, addr, start):
	global serversocket, file_extension, c_get, conn, SIZE, lthread, SERVER, MAIN, scode
	c_get = False
	f_flag = 0
	filedata = b""
	conn = True
	urlflag = 0
	while conn and SERVER and MAIN:
		message = connectionsocket.recv(SIZE)
		try:
			message = message.decode('utf-8')
			req_list = message.split('\r\n\r\n')
			f_flag = 0
		except UnicodeDecodeError:
			req_list = message.split(b'\r\n\r\n')
			req_list[0] = req_list[0].decode(errors = 'ignore')
			f_flag = 1
		if len(req_list) > 1:
			pass
		else:
			break
		try:
			log.write(((addr[0]) + '\n' + req_list[0] + '\n\n'))
		except:
			pass
		display = []
		header_list = req_list[0].split('\r\n')
		header_len = len(header_list)
		ent_body = req_list[1]
		request_line = header_list[0].split(' ')
		method = request_line[0]
		element = request_line[1]
		if element == favicon:
			element = FAVICON
		elif element == '/':
			element = os.getcwd()
		element, query = resolve(element)
		if (len(element) > MAX_URL and urlflag == 0):
			status(connectionsocket, 414)
			break
		else:
			urlflag = 1
		version = request_line[2]
		try:
			version_num = version.split('/')[1]
			if not (version_num == RUNNING_VERSION):
				status(connectionsocket, 505)
		except IndexError:
			status(connectionsocket, 505)
		switcher = {}
		request_line = header_list.pop(0)
		for line in header_list :
			line_list = line.split(': ')
			switcher[line_list[0]] = line_list[1]
		if method == 'GET' or method == 'HEAD':
			method_get_head(connectionsocket, element, switcher, query, method)
		elif method == 'POST':
			method_post(ent_body, connectionsocket, switcher)
		elif method == 'PUT':
			display = method_put(connectionsocket, addr, ent_body, filedata, element, switcher, f_flag)
			encoded = '\r\n'.join(display).encode()
			connectionsocket.send(encoded)
		elif method == 'DELETE':
			method_delete(element, connectionsocket, ent_body, switcher)
			conn = False
			connectionsocket.close()
		elif method == 'CONNECT':
			method_connect(connectionsocket, switcher)
			conn = True
		elif method == 'OPTIONS':
			method_option(element, connectionsocket, switcher)
			conn = False
			connectionsocket.close()
		elif method == 'TRACE':
			method_trace(req_list[0], connectionsocket, switcher)
			conn = False
			connectionsocket.close()
		else:
			method = ''
			break
		logging.info('	{}	{}	{}	{}	{}\n'.format(addr[0], addr[1], request_line, element, scode))
	try:
		connectionsocket.close()
		lthread.remove(connectionsocket)
	except:
		pass

#function handling multiple requests
def server():
	global SERVER, MAIN, lthread
	while MAIN:
		while SERVER:
			if not MAIN:
				break
			start = 0
			connectionsocket, addr = serversocket.accept()
			lthread.append(connectionsocket)
			if(len(lthread) < MAX_REQUESTS):
				start_new_thread(clientfun, (connectionsocket, addr, start))
			else:
				status(connectionsocket, 503)
				connectionsocket.close()
	serversocket.close()
	

# function to find the server's ip address
def findip():
	try:
		s.connect(('8.8.8.8', 8000))
		IP = s.getsockname()[0]
	except:
		IP = '127.0.0.1'
	s.close()
	return IP

def manage_server():
	global SERVER, MAIN, conn
	while True:
		string = input()
		if string == 'stop':
			SERVER = False
		elif string == 'restart':
			SERVER = True
		elif string == 'close':
			MAIN = False
			conn = False
			break

# function main
if __name__ == '__main__':
	ip = str(findip())
	try:
		serverport = int(sys.argv[1])
	except:
		print('Usage: python3 webserver.py port_number(valid)')
		sys.exit()
	try:
		serversocket.bind(('', serverport))
	except:
		print('HTTPServer invalid arguements')
		print('Usage: python3 webserver.py port_number(valid)')
		sys.exit()
	serversocket.listen(40)
	print('Serving HTTP on ' + ip + ' port ' + str(serverport) + ' (http://' + ip + ':' + str(serverport) +'/)')
	start_new_thread(manage_server, ())
	server()
	sys.exit()
#end to server implementation
