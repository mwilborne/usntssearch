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

from flask import  Flask, render_template, redirect, Response, send_file
import tempfile
import os
import requests
import megasearch
import datetime
import time
import urllib2
import threading
import logging
import base64
import SearchModule


from random import shuffle,seed

log = logging.getLogger(__name__)

#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~
class Warper:

	# Set up class variables
	def __init__(self,cgen):
		self.base64scramble_enc={
            'A':['A',0],'B':['B',1],'C':['C',2],'D':['D',3],'E':['E',4],'F':['F',5] ,
            'G':['G',6],'H':['H',7],'I':['I',8],'J':['J',9],'K':['K',10],'L':['L',11],
            'M':['M',12],'N':['N',13],'O':['O',14],'P':['P',15],'Q':['Q',16],'R':['R',17],
            'S':['S',18],'T':['T',19],'U':['U',20],'V':['V',21],'W':['W',22],'X':['X',23],
            'Y':['Y',24],'Z':['Z',25],
			'a':['a',26+0],'b':['b',26+1],'c':['c',26+2],'d':['d',26+3],'e':['e',26+4],'f':['f',26+5],
            'g':['g',26+6],'h':['h',26+7],'i':['i',26+8],'j':['j',26+9],'k':['k',26+10],'l':['l',26+11],
            'm':['m',26+12],'n':['n',26+13],'o':['o',26+14],'p':['p',26+15],'q':['q',26+16],'r':['r',26+17],
            's':['s',26+18],'t':['t',26+19],'u':['u',26+20],'v':['v',26+21],'w':['w',26+22],'x':['x',26+23],
            'y':['y',26+24],'z':['z',26+25],
            '0':['0',52],'1':['1',53],'2':['2',54],'3':['3',55],'4':['4',56],'5':['5',57],
            '6':['6',58],'7':['7',59],'8':['8',60],'9':['9',61]
            #~ ,'+':['+',62],'/':['/',63]
            }
		self.seedno = cgen['seed_warptable']
		self.base64scramble_dec = self.base64scramble_enc
		self.generate_hashtable()
		print '>> Hash table has been initialized: ' + str(self.seedno)
		
		#~ encstrhash = self.chash64_encode('pillone@mailub')
		#~ print '===='
		#~ print encstrhash
		#~ decstrhash = self.chash64_decode(encstrhash)
		#~ print decstrhash
		#~ print '===='
		#~ print self.base64scramble_enc
		#~ print self.base64scramble_dec
#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~


	def chash64_decode(self, enc_str):
		nstr = ''
		for i in xrange(len(enc_str)):
			nstr += self.base64scramble_dec[ enc_str[i] ] [0]
		dec_str_b64 = base64.b64decode(nstr)
		#~ print 	enc_str
		#~ print 	nstr
		#~ print 	dec_str_b64
		return dec_str_b64
#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~

	def chash64_encode(self, str):
		enc_str_b64 = base64.b64encode(str)
		nstr = ''
		for i in xrange(len(enc_str_b64)):
			nstr += self.base64scramble_enc[ enc_str_b64[i] ] [0]
		#~ print str	
		#~ print enc_str_b64
		#~ print nstr		
		return nstr
#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~
		
	def generate_hashtable(self):
		seed(self.seedno)
		#~ encoder table
		self.base64scramble_enc_inv= [i for i in range(len(self.base64scramble_enc))]
		for key in self.base64scramble_enc.keys():
			idx = self.base64scramble_enc[key][1]
			self.base64scramble_enc_inv[idx] = self.base64scramble_enc[key][0]

		s = [i for i in range(len(self.base64scramble_enc))]
		shuffle(s)
		#~ print s
		
		for i in range(len(s)):
			aidx_s = self.base64scramble_enc_inv[i]
			aidx_d = self.base64scramble_enc_inv[s[i]]
			self.base64scramble_enc[aidx_s][0] = aidx_d
		#~ dencoder table
		self.base64scramble_dec= {}
		for key in self.base64scramble_enc.keys():
			ikey = self.base64scramble_enc[key][0] 
			self.base64scramble_dec[ikey] = [key, self.base64scramble_enc[key][1]]

		self.base64scramble_enc['+'] = ['+', len(s)+1]
		self.base64scramble_dec['+'] = ['+', len(s)+1]

		self.base64scramble_enc['/'] = ['-', len(s)+2]
		self.base64scramble_dec['-'] = ['/', len(s)+2]

		self.base64scramble_enc['='] = ['=', len(s)+3]
		self.base64scramble_dec['='] = ['=', len(s)+3]

#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~
	def beam_cookie(self, urltouse, args):
		retfail = -1
		
		global globalResults
		
		if 'loadedModules' not in globals():
			SearchModule.loadSearchModules()
		
		cookie = {}
		for module in SearchModule.loadedModules:
			if( module.typesrch == args['m']):
				if(module.dologin() == True):
					cookie =  module.cookie
				else: 
					return retfail
				
 		try:
			opener = urllib2.build_opener()
			opener.addheaders.append(('Cookie', 'FTDWSESSID='+cookie['FTDWSESSID']))
			response = opener.open(urltouse)

		except Exception as e:
			return retfail
 		
		fcontent = response.read()
		#~ print response.info()
		f=tempfile.NamedTemporaryFile(delete=False)
		f.write(fcontent)
		f.close()	
		fresponse = send_file(f.name, mimetype='application/x-nzb;', as_attachment=True, 
						attachment_filename='yourmovie.nzb', add_etags=False, cache_timeout=None, conditional=False)
		os.remove(f.name)
		
		for i in xrange(len(response.info().headers)):
			if(response.info().headers[i].find('Content-Encoding')  != -1):
				fresponse.headers["Content-Encoding"] = 'gzip'
				break
		fresponse.headers['Content-Disposition'] = response.headers['Content-Disposition']
		return fresponse	

#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~

				
	def beam_notenc(self, urltouse):

		response = Response('Hey there!')
		response.headers['X-Accel-Redirect'] = '/warpme/'+urltouse
		response.headers['Content-Type'] = 'application/x-nzb;'
		
		return response

#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~
		
	def beam(self, arguments):

		#~ manual proxing 
		if('m' in arguments and 'x' in arguments):
			decodedurl = self.chash64_decode(arguments['x'])
			response = self.beam_cookie(decodedurl, arguments)
			log.info ('WARPNGX: ' + decodedurl + ' --> manual cookie')	
			return response				

		#~ turbo nginxproxing 	
		if('x' in arguments):
			decodedurl = self.chash64_decode(arguments['x'])
			#~ print decodedurl
			response = self.beam_notenc(decodedurl)
			if('y' in arguments):
				log.info ('RAWNGXY: '+str(arguments['x'])+'--y='+str(arguments['y']))
			else:
				log.info ('RAWNGXN: '+arguments['x'])	
			log.info ('WARPNGX: ' + decodedurl + ' --> ' + response.headers['X-Accel-Redirect'])	
			#~ print response.headers['X-Accel-Redirect']
			
			return response	
	
