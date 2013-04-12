# # ## # ## # ## # ## # ## # ## # ## # ## # ## # ## # ## # ## # ## # ## #    
#~ This file is part of NZBmegasearch by 0byte.
#~ 
#~ NZBmegasearch is free software: you can redistribute it and/or modify
#~ it under the terms of the GNU General Public License as published by
#~ the Free Software Foundation, either version 3 of the License, or
#~ (at your option) any later version.
#~ 
#~ NZBmegasearch is distributed in the hope that it will be useful,
#~ but WITHOUT ANY WARRANTY; without even the implied warranty of
#~ MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#~ GNU General Public License for more details.
#~ 
#~ You should have received a copy of the GNU General Public License
#~ along with NZBmegasearch.  If not, see <http://www.gnu.org/licenses/>.
# # ## # ## # ## # ## # ## # ## # ## # ## # ## # ## # ## # ## # ## # ## #    

import re
import time
import tempfile
import datetime
import mechanize
import sys, logging
import cookielib
from BeautifulSoup  import BeautifulSoup 
import config_settings
from urllib2 import urlparse
import socket
import locale

MAXTIMEOUT=10
log = logging.getLogger(__name__)

class DeepSearch:

	def __init__(self, cur_cfg, cgen):
		
		self.ds = []
		count  = 0
		for cfg in cur_cfg:
			self.ds.append(DeepSearch_one(cfg, cgen))
			self.ds[count].typesrch = 'DSN' + str(count)
			count = count + 1

	#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ 	
class DeepSearch_one:
	
	#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ 
	def __init__(self, cur_cfg, cgen):
		self.br = mechanize.Browser(factory=mechanize.RobustFactory())
		self.cj = cookielib.LWPCookieJar()
		self.br.set_cookiejar(self.cj)
		self.br.set_handle_equiv(True)
		self.br.set_handle_redirect(False)
		self.br.set_handle_referer(True)
		self.br.set_handle_robots(False)
		self.br.addheaders = [('User-agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1')]
		self.cur_cfg = cur_cfg
		self.timeout = cgen['default_timeout']
		self.baseURL = self.cur_cfg['url']
		#~ print self.cur_cfg['url']
		humanprovider = urlparse.urlparse(self.baseURL).hostname			
		self.name = humanprovider.replace("www.", "")
		self.basic_sz = 1024*1024
		self.dologin()
		self.typesrch = 'DSNINIT'

	#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ 

	def reset_cookies(self):
		self.cj = cookielib.LWPCookieJar()
		self.br.set_cookiejar(self.cj)

	#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ 

	def mech_error_generic (self, e):
		if(str(e).find("Errno 111") != -1):
			print "Wrong url or site down " + self.baseURL
			log.warning("Wrong url or site down " + self.baseURL)
			return 111
		if(str(e).find("timed out") != -1):
			print "Too much time to respond "  + self.baseURL
			log.warning("Too much time to respond "  + self.baseURL)
			return 500
		if(str(e).find("HTTP Error 302") == -1):
			log.warning("Fetched exception login: " + str(e) + self.baseURL)
			return 302
		print "Fetched exception: "  + self.baseURL + str(e)
		log.warning("Fetched exception: "  + self.baseURL + str(e))
		return 440


	#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ 
	def chkcookie(self):
		cexp = True
		for cookie in self.br._ua_handlers['_cookies'].cookiejar:
			#~ print self.br._ua_handlers['_cookies'].cookiejar
			if( cookie.is_expired() ) :
				cexp = False
		#~ print len(self.br._ua_handlers['_cookies'].cookiejar)		
		if(len(self.br._ua_handlers['_cookies'].cookiejar) == 0):
			cexp = False
		return cexp

	#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ 	
	def dologin(self):
				
		socket.setdefaulttimeout(self.timeout)
		if	( self.chkcookie() == True):
			return True
		mainurl = self.cur_cfg['url']
		loginurl = mainurl + "/login"

		print "Logging in: " + mainurl
		log.info("Logging in: " + mainurl)

		
		try:
			self.br.open(loginurl)
			print loginurl			
		except Exception as e:
			print str(e)
			self.mech_error_generic(e)
			return False
		
		formcount=0
		formfound=False
		for frm in self.br.forms():  
			#~ print frm.action
			if (frm.action.find("login") != -1):
				formfound = True
				break
			formcount=formcount+1
				
		if(	formfound == False):
			return False

		self.br.select_form(nr=formcount)
		self.br["username"] = self.cur_cfg['user']
		self.br["password"] = self.cur_cfg['pwd']
		try:
			response2 = self.br.submit()
		except Exception as e:
			if(str(e).find("timed out") != -1):
				log.warning("Down or timeout: " + mainurl)
				#~ print "Down or timeout"
				return False
			if(str(e).find("HTTP Error 302") == -1):
				#~ print "Fetched exception login: " + str(e) 	
				log.warning("Fetched exception login: " + str(e) + mainurl)
				return False

		#~ eternal cookies
		#~ for cookie in self.br._ua_handlers['_cookies'].cookiejar:
			#~ print cookie
			#~ cookie.expires = None

		return True		

	#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ 
	
	def get_profile_info(self):
		socket.setdefaulttimeout(self.timeout)
		if	(self.chkcookie() == False):
			if(self.dologin() == False):
				return []

		loginurl = self.cur_cfg['url'] + "/profile"
		try:
			res = self.br.open(loginurl)
		except Exception as e:
			eret = self.mech_error_generic(e)
			if(eret == 302):
				self.reset_cookies()
			return []

		data = res.get_data()  
		soup = BeautifulSoup(data)

		info = {}
		for row in soup.findAll("tr"):
			data = {}
			#~ print row
			#~ print '--------'
			allTHs = row.findAll("th")
			for x in range(len(allTHs)):
				str_lowcase = str(allTHs[x]).lower()
				if(str_lowcase.find('api hits today') > -1):
					allTD = row.findAll("td")
					if(len(allTD)):
						info['api_hits'] = ''.join(allTD[0].findAll(text=True))
						
				if(str_lowcase.find('grabs today') > -1):	
					allTD = row.findAll("td")
					if(len(allTD)):
						info['grabs_today'] =  ''.join(allTD[0].findAll(text=True))
				if(str_lowcase.find('grabs total') > -1 or str_lowcase.find('grabs') > -1):	
					allTD = row.findAll("td")
					if(len(allTD)):
						info['grabs_total'] =  ''.join(allTD[0].findAll(text=True))

		print info		
		return info

	#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ 					
	def download(self, urlname):
		socket.setdefaulttimeout(self.timeout)

		if	(self.chkcookie() == False):
			if(self.dologin() == False):
				return ''
		try:
			#~ print urlname
			res = self.br.open(urlname)
			return res
		except Exception as e:
			self.mech_error_generic(e)
			return ''

		#~ fname = tempfile.mktemp ()
		#~ try:
			#~ self.br.retrieve(urlname,fname)[0]
			#~ return fname
		#~ except Exception as e:
			#~ log.warning(str(e) + " Failed to dowload : " + urlname)
			#~ return ''

	#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ 					

	def search(self, srchstr):
		socket.setdefaulttimeout(self.timeout)
		locale.setlocale( locale.LC_ALL, 'en_US.utf8' )

		if	(self.chkcookie() == False):
			if(self.dologin() == False):
				return []

		mainurl = self.cur_cfg['url']
		loginurl = mainurl + "/search/"+srchstr
		timestamp_s = time.time()	
		try:
			res = self.br.open(loginurl)
		except Exception as e:
			self.mech_error_generic(e)
			eret = self.mech_error_generic(e)
			if(eret == 302):
				self.reset_cookies()
			return []

		data = res.get_data()  
		timestamp_e = time.time()
		print mainurl + " " + str(timestamp_e - timestamp_s)

		soup = BeautifulSoup(data)

	#~ def searchDBG(self, srchstr):
		#~ handler = open('tmp/tater.html').read()
		#~ soup = BeautifulSoup (handler)
		
		parsed_data = []
		titles = soup.findAll('a', {'class': 'title'})
		nzburls = soup.findAll('a', {'title': 'Download Nzb'})
		tstamp_raw = soup.findAll('td', {'class': 'less mid'})
		rdetails = soup.findAll('a', {'title': 'View details'})
		sz_raw = soup.findAll('td', {'class': 'less right'})

		bytesize = []
		for sz1 in sz_raw:
			#~ rawline = str(sz1).split()
			for sz2 in sz1.findAll(text=True):
				sz2s =  sz2.split()
				

				if(len(sz2s) == 2):
					#~ print sz2s[1].lower()
					if (sz2s[1].lower() == 'mb' ):
						bytesize.append(int(self.basic_sz * locale.atof(sz2s[0])))
					if (sz2s[1].lower() == 'gb' ):
						bytesize.append(int(self.basic_sz * locale.atof(sz2s[0]) * 1024))
		#~ print bytesize

		#~ 2010-05-08 18:53:09
		tstamp = []
		for tt in tstamp_raw:
			for tt2 in tt.attrs:
				#~ print tt2[1]
				if('title' in tt2):
					tstamp.append( time.mktime(datetime.datetime.strptime(tt2[1], "%Y-%m-%d %H:%M:%S").timetuple()) )

		if(len(titles) != len(nzburls)):
			return []
		if(len(titles) != len(tstamp)):
			return []
		if(len(titles) != len(rdetails)):
			return []
		if(len(titles) != len(bytesize)):
			return []
			

		for i in xrange(len(titles)):
			d1 = {
				'title': ''.join(titles[i].findAll(text=True)),
				'poster': 'poster',
				'size': bytesize[i],
				'url': self.baseURL + '/' + nzburls[i]['href'],
				'filelist_preview': '',
				'group': 'N/A',
				'posting_date_timestamp': tstamp[i],
				'release_comments': self.baseURL + '/' +rdetails[i]['href'],
				'categ':{'N/A':1},
				'ignore':0,
				'req_pwd':self.typesrch,
				'provider':self.baseURL,
				'providertitle':self.name
			}
			#~ print d1
			parsed_data.append(d1)
		
		
		return parsed_data
		
