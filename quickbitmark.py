#!/usr/bin/env python

import urllib2, urllib, base64, json, sys, shelve, subprocess
from contextlib import closing
from getpass import getpass
from argparse import ArgumentParser

API = "https://api-ssl.bitly.com"
YELLOW = '\033[33m'
CYAN = '\033[36m'
ENDC = '\033[0m' 


def authenticate(user,pwd):
	value = "Basic " + base64.b64encode(user + ":" + pwd)
	headers = {'Authorization': value}
	url = API + "/oauth/access_token"
	req = urllib2.Request(url, 'True', headers)
	try:
		response = urllib2.urlopen(req)
		content = response.read()
	except urllib2.HTTPError, error:
		content = False
	return content


def login():
	with closing(shelve.open('settings.conf')) as settings:
		if 'FIRST_USE' not in settings:
			settings['FIRST_USE'] = True

		if settings['FIRST_USE']:
			while True:
				user = raw_input('username: ')
				pwd = getpass('password: ')
				token = authenticate(user, pwd)
				if token:
					break
				print "Wrong credentials. Try again.\n"
			save = raw_input('save credentials? (Y/N): ')
			if save.strip().upper() == 'Y':
				settings['MYTOKEN'] = str(token)
				settings['FIRST_USE'] = False
			return token
		else:
			return settings['MYTOKEN']


def shorten(longurl, token):
	longurl_clean = urllib.quote_plus(longurl.strip())
	req = urllib2.Request(API + '/v3/shorten/?access_token=' + token + 
		'&longUrl=' + longurl_clean)
	response = urllib2.urlopen(req)
	out = json.loads(response.read())
	return out['data']['url']


def copypaste(shorturl):
	if sys.platform == 'darwin':
		p = subprocess.Popen(["pbcopy"],stdin=subprocess.PIPE)
		p.stdin.write(shorturl)
		print "(short URL copied to your clipboard)\n" + ENDC
	elif sys.platform == 'linux' or sys.platform == 'linux2':
		p = subprocess.Popen(["xclip -selection clipboard -i"],
			stdin=subprocess.PIPE)
		p.stdin.write(shorturl)
		print "(short URL copied to your clipboard)\n" + ENDC
	else:
		print ENDC


if __name__ == '__main__':
	parser = ArgumentParser(description='Generate bit.ly short URLs.')
	parser.add_argument("URL", nargs="?", default=False, help="URL to shorten")
	parser.add_argument("-r", "--reset", action="store_true", 
		help="Use this option to reset or change your credentials.")
	options = parser.parse_args()
	token = login()
	if options.reset:
		with closing(shelve.open('settings.conf')) as settings:
			settings['FIRST_USE'] = True
			settings['MYTOKEN'] = ""
		sys.exit(0)
	elif options.URL:
		longurl = sys.argv[1]
	else:
		longurl = str(raw_input('URL: '))

	shorturl = shorten(longurl, token)
	print YELLOW + "Shortened URL: " + shorturl
	copypaste(shorturl)
