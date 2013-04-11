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

from flask import Flask
from flask import request, Response, redirect
import logging
import logging.handlers
import os
import threading
import SearchModule
import DeepsearchModule
from ApiModule import ApiResponses
from SuggestionModule import SuggestionResponses
from WarperModule import Warper
import megasearch
import config_settings
import miscdefs
import random
import time

DEBUGFLAG = False

motd = '\n\n~*~ ~*~ NZBMegasearcH ~*~ ~*~'
print motd

#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ 
cfg,cgen = config_settings.read_conf()
cfg_deep = config_settings.read_conf_deepsearch()
logsdir = SearchModule.resource_path('logs/')
logging.basicConfig(filename=logsdir+'nzbmegasearch.log',level=logging.INFO,format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
log = logging.getLogger(__name__)
handler = logging.handlers.RotatingFileHandler(logsdir+'nzbmegasearch.log', maxBytes=cgen['log_size'], backupCount=cgen['log_backupcount'])
log.addHandler(handler)
log.info(motd)
templatedir = SearchModule.resource_path('templates')
app = Flask(__name__, template_folder=templatedir)	
cver_ver_notify= { 'chk':1, 
			  'curver': '--' }
print '>> version: '+ str(cver_ver_notify['curver'])
SearchModule.loadSearchModules()
if(DEBUGFLAG):
	cgen['general_trend'] = 0
	print 'MEGA2: DEBUGFLAG MUST BE SET TO FALSE BEFORE DEPLOYMENT'
sugg = SuggestionResponses(cfg, cgen)
#~ detached server for trends
sugg.detached_trendpolling = 1

#~ wait for login init
if(DEBUGFLAG == False):
	random.seed()
	sleeptime = random.randrange(0, 10)
	log.info('Wait ' + str(sleeptime) + 's for initialization...')
	time.sleep(sleeptime)	
ds = DeepsearchModule.DeepSearch(cfg_deep, cgen)

mega_parall = megasearch.DoParallelSearch(cfg, cgen, ds)
wrp = Warper (cgen, ds)
apiresp = ApiResponses(cfg, wrp)
dwn = miscdefs.DownloadedStats()
#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ 


@app.route('/sts_dwnl_gnr')
def dstastprovide():	
	return dwn.get(request.args)
	

@app.route('/legal')
def legal():
	return (miscdefs.legal())
	
		
#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ 

@app.route('/s', methods=['GET'])
def search():
	
	sugg.asktrend_allparallel()	
	#~ parallel suggestion and search
	if(DEBUGFLAG == False):
		t1 = threading.Thread(target=sugg.ask, args=(request.args,) )
	t2 = threading.Thread(target=mega_parall.dosearch, args=(request.args,)   )
	if(DEBUGFLAG == False):
		t1.start()
	t2.start()
	if(DEBUGFLAG == False):	
		t1.join()
	t2.join()

	params_dosearch = {'args': request.args, 
						'sugg': sugg.sugg_info, 
						'configr': cfg,
						'trend_movie': sugg.movie_trend, 
						'trend_show': sugg.show_trend, 
						'ver': cver_ver_notify,
						'wrp':wrp,
						'debugflag':DEBUGFLAG
						}
	return mega_parall.renderit(params_dosearch)

#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ 
@app.route('/config', methods=['GET','POST'])
def config():
	return config_settings.config_read()


#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ 

@app.route('/warp', methods=['GET'])
def warpme():
	res = wrp.beam(request.args)
	
	if(res == -1):
		return main_index()
	else: 	
		return res

#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ 
			
@app.route('/', methods=['GET','POST'])
def main_index():
	sugg.asktrend_allparallel()
	params_dosearch = {'args': '', 
						'sugg': [], 
						'trend': [], 
						'configr': cfg,
						'trend_movie': sugg.movie_trend, 
						'trend_show': sugg.show_trend, 
						'ver': cver_ver_notify,
						'debugflag':DEBUGFLAG}
	return mega_parall.renderit_empty(params_dosearch)

#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ 

@app.route('/api', methods=['GET'])
def api():
	#~ print request.args
	return apiresp.dosearch(request.args)

@app.route('/connect', methods=['GET'])
def connect():
	return miscdefs.connectinfo()
 
#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~   

@app.errorhandler(404)
def generic_error(error):
	return main_index()
 

if __name__ == "__main__":	
	sugg.asktrend_allparallel()
	chost = '0.0.0.0'
	cport = int(cgen['portno'])
	print '>> Running on port '	+ str(cport)

	app.run(host=chost,port=cport, debug = DEBUGFLAG)
