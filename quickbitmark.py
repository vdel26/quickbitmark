import urllib2, urllib, base64, json
import subprocess
from urlparse import urlparse
from getpass import getpass

API = "https://api-ssl.bitly.com"
YELLOW = '\033[33m'
CYAN = '\033[36m'
ENDC = '\033[0m' 

def authenticate(user,pwd):
	value = "Basic " + base64.b64encode(user + ":" + pwd)
	headers = {'Authorization': value}
	url = API + "/oauth/access_token"
	req = urllib2.Request(url, 'True', headers)
	response = urllib2.urlopen(req)
	return response.read()

def get_account(token):
	req = urllib2.Request(API + "/v3/user/info?access_token=" + token)
	response = urllib2.urlopen(req)
	out = json.loads(response.read())
	return out['data']['login']

def shorten(longurl, token):
	#longurl_parsed = urlparse(longurl)
	#if longurl_parsed.path[0] != '/':
	#	pass
	params = {'access_token': token, 'longUrl': longurl}
	req = urllib2.Request(API + '/v3/shorten/?access_token=' + token + '&longUrl=' + longurl)
	response = urllib2.urlopen(req)
	out = json.loads(response.read())
	return out['data']['url']

if __name__ == '__main__':
	user = raw_input('username: ')
	pwd = getpass('password: ')
	token = authenticate(user, pwd)
	#print get_account(token)
	longurl = str(raw_input('URL: '))
	shorturl = shorten(longurl, token)
	print YELLOW + "Shortened URL: " + shorturl + ENDC
	p = subprocess.Popen(["pbcopy"],stdin=subprocess.PIPE)
	p.stdin.write(shorturl)

