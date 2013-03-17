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


from flask import  Flask, render_template, redirect, send_file, Response
import requests
import tempfile
import megasearch
import xml.etree.ElementTree
import xml.etree.cElementTree as ET
import SearchModule
import datetime
import base64
import urllib2
import os
import logging

log = logging.getLogger(__name__)

#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~
class ApiResponses:

	# Set up class variables
	def __init__(self, conf, wrp):
		self.response = []
		self.cfg= conf
		self.timeout = conf[0]['timeout']
		self.serie_string = ''
		self.typesearch = ''
		self.wrp = wrp
		self.tvrage_rqheaders = {
								'Connection': 'keep-alive;' ,
								'Cache-Control': 'max-age=0',
								'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
								'User-Agent': 'Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1312.52 Safari/537.17',
								'Referer': 'http://services.tvrage.com/info.php?page=main',
								'Accept-Encoding': 'gzip,deflate,sdch',
								'Accept-Language': 'en-US,en;q=0.8',
								'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3'
								 }
						 		
	def dosearch(self, arguments):
		self.args = arguments
		
		if(self.args.has_key('t')):
			typesearch=self.args['t']
			if (typesearch == 'tvsearch'):
				response = self.sickbeard_req()
			elif (typesearch == 'movie'):
				response = self.couchpotato_req()	
			#~ elif (typesearch == 'music'):
				#~ response = self.headphones_req()	
			elif (typesearch == 'get'):	
				filetosend = self.proxy_NZB_file()
				return filetosend
			else:
				print '>> UNKNOWN REQ -- ignore' 
				response = render_template('api_error.html')
		else:
			response = render_template('api_error.html')
		return response	

	#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~
	def headphones_req(self):	
		print self.args
		if(self.args.has_key('album') or self.args.has_key('artist')  or self.args.has_key('track')):
			return self.generate_music_nabresponse()
		else:	
			return render_template('api_error.html')
			
	#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~

	def generate_music_nabresponse(self):
		dstring = []
		if(self.args.has_key('artist')):
			dstring.append(SearchModule.sanitize_strings(self.args['artist']))
		if(self.args.has_key('album')):
			dstring.append(SearchModule.sanitize_strings(self.args['album']))
		if(self.args.has_key('track')):
			dstring.append(SearchModule.sanitize_strings(self.args['track']))
		if(self.args.has_key('year')):
			dstring.append(SearchModule.sanitize_strings(self.args['year']))
			
		music_search_str = ''	
		for i in xrange(len(dstring)):
			if(len(dstring[i]) and i<len(dstring)-1):
				music_search_str = music_search_str + dstring[i]
		
		print music_search_str
		#~ print movie_search_str
		self.searchstring = music_search_str
		self.typesearch = 0
		#~ compile results				
		#~ results = SearchModule.performSearch(movie_search_str, self.cfg )		
		#~ flatten and summarize them
		#~ cleaned_results = megasearch.summary_results(results,movie_search_str)
		#~ render XML
		#~ return self.cleanUpResultsXML(cleaned_results)
		return 'm'
	
	#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~		
		
	def proxy_NZB_file(self):
		fullurl = base64.b64decode(self.args['id'])
		return self.wrp.beam_notenc(fullurl)

		#~ LOCAL VERSION
		'''
		response = urllib2.urlopen(fullurl)
		fcontent = response.read()
		#~ print fullurl
		#~ print response.info()
		
		f=tempfile.NamedTemporaryFile(delete=False)
		f.write(fcontent)
		f.close()	
		fresponse = send_file(f.name, mimetype='application/x-nzb;', as_attachment=True, 
						attachment_filename='yourmovie.nzb', add_etags=False, cache_timeout=None, conditional=False)
		os.remove(f.name)
		#~ not needed
		#~ print response.info()
		#~ brutal but works
		for i in xrange(len(response.info().headers)):
			if(response.info().headers[i].find('Content-Encoding')  != -1):
				fresponse.headers["Content-Encoding"] = 'gzip'
				break
		#~ print fresponse.headers
		return fresponse				

		'''
		

	#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~
	def couchpotato_req(self):	
	
		if(self.args.has_key('imdbid')):
			# print 'requested movie ID'
			#~ request imdb
			#~ http://deanclatworthy.com/imdb/?id=tt1673434
			#~ http://imdbapi.org/?id=tt1673434
			imdb_show = self.imdb_movieinfo(self.args['imdbid'])	
			if(len(imdb_show['movietitle'])): 
				return self.generate_movie_nabresponse(imdb_show)
			else:
				return render_template('api_error.html')		
		else:
			return render_template('api_default.html')
			
			
	#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~
	def sickbeard_req(self):	
		if(self.args.has_key('rid')):
			#~ print 'requested series ID'
			#~ request rage
			tvrage_show = self.tvrage_getshowinfo(self.args['rid'])	
			if(len(tvrage_show['showtitle'])): 
				return self.generate_tvserie_nabresponse(tvrage_show)				
			else:
				return render_template('api_error.html')		
		else:
			return render_template('api_default.html')

	#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~


	def imdb_movieinfo(self, mid):	
		parsed_data = {'movietitle': '',
						'year': '1900'}

		url_imdb  = 'http://imdbapi.org/'
		urlParams = dict( id= 'tt' + mid)
		#~ loading
		try:
			http_result = requests.get(url=url_imdb , params=urlParams, verify=False, timeout=self.timeout)
		except Exception as e:
			print e
			log.critical(str(e))
			return parsed_data
		
		try:
			data = http_result.json()
		except Exception as e:
			print e
			log.critical(str(e))	
			return parsed_data
			
		parsed_data = { 'movietitle': data['title'],
						'year': str(data['year'])}
		#~ print parsed_data

		return parsed_data
	#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~


	def tvrage_getshowinfo(self, rid ):	
		parsed_data = {'showtitle': ''}

		url_tvrage = 'http://www.tvrage.com/feeds/showinfo.php'
		urlParams = dict( sid=rid )			
		#~ loading
		try:
			http_result = requests.get(url=url_tvrage, params=urlParams, verify=False, timeout=self.timeout,  headers=self.tvrage_rqheaders)
		except Exception as e:
			print e
			log.critical(str(e))
			return parsed_data
		
		data = http_result.text
		#~ parsing
		try:
			tree = ET.fromstring(data.encode('utf-8'))
		except Exception as e:
			print e
			log.critical(str(e))
			return parsed_data

		showtitle = tree.find("showname")	
		if(showtitle is not None):
			parsed_data['showtitle'] = showtitle.text
		
		return parsed_data

	#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~

	def generate_movie_nabresponse(self,imdb_show ):

		movie_search_str = imdb_show['movietitle'].lower().replace("'", "").replace("-", " ").replace(":", " ")
		movie_search_str = " ".join(movie_search_str.split()).replace(" ", ".") + '.' +imdb_show['year']
		
		#~ print movie_search_str
		self.searchstring = movie_search_str
		self.typesearch = 0
		#~ compile results				
		results, ignoreck = SearchModule.performSearch(movie_search_str, self.cfg )		
		#~ flatten and summarize them
		cleaned_results = megasearch.summary_results(results,movie_search_str)
		#~ render XML
		return self.cleanUpResultsXML(cleaned_results)
		
	#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~

	def generate_tvserie_nabresponse(self,tvrage_show ):
		#~ compile string
		season_num = self.args.get('season',-1, type=int)
		serie_search_str = SearchModule.sanitize_strings(tvrage_show['showtitle'])
		if(self.args.has_key('ep')):
			ep_num = self.args.get('ep',-1, type=int)			
			serie_search_str = serie_search_str + '.s%02d' % season_num + 'e%02d' % ep_num
		else:	
			serie_search_str = serie_search_str + '.s%02d' % season_num 
		self.typesearch = 1
		self.searchstring = serie_search_str
		#~ compile results				
		results, ignoreck = SearchModule.performSearch(serie_search_str, self.cfg )		
		#~ flatten and summarize them
		cleaned_results = megasearch.summary_results(results,serie_search_str)
		#~ render XML
		return self.cleanUpResultsXML(cleaned_results)

	
	
	#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~
	def crude_subcategory_identifier(self, titlestring):
		idx1=titlestring.find('720p')
		idx2=titlestring.find('1080p')
		hires = False
		
		if(idx1 != -1 or idx2 != -1):
			hires = True
		
		if(self.typesearch == 0):
			if(hires == True):
				return 2040
			else:	
				return 2030

		if(self.typesearch == 0):
			if(hires == True):
				return 5040
			else:	
				return 5030
	
	
	#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~
	
	
	# Generate XML for the results
	def cleanUpResultsXML(self, results):
		niceResults = []
		#~ no sorting
		for i in xrange(len(results)):
			if(results[i]['ignore'] == 0):
				dt1 =  datetime.datetime.fromtimestamp(int(results[i]['posting_date_timestamp']))
				human_readable_time = dt1.strftime("%a, %d %b %Y %H:%M:%S")
				#~ nobody parses it
				#~ category = self.crude_subcategory_identifier(results[i]['title'])
				#~ print human_readable_time
				niceResults.append({
					'url': results[i]['url'],
					'encodedurl': base64.b64encode(results[i]['url']),
					'title':results[i]['title'],
					'filesize':results[i]['size'],
					'age':human_readable_time,
					'providertitle':results[i]['providertitle'],
					'providerurl':results[i]['provider']
				})
		
		kindofreq = datetime.datetime.now().strftime("%Y-%m-%d %H:%M ") 
		idbinfo = ''
		if(self.typesearch == 0):
			idbinfo = self.args['imdbid']
			kindofreq = kindofreq + ' CP '
		if(self.typesearch == 1):
			idbinfo = ''
			kindofreq = kindofreq + ' SB ' + self.args['rid'] + ' '
			
		mssg = kindofreq + self.searchstring + ' ' + str(len(niceResults)) + ' ' +  str(len(results))
		print mssg
		log.info (mssg)
		return render_template('api.html',results=niceResults, num_results=len(niceResults), typeres= self.typesearch, idb = idbinfo)
	
