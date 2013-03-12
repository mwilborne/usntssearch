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
import os
import threading
from SuggestionModule import SuggestionResponses
import config_settings
import SearchModule
import logging
import logging.handlers
import time

DEBUGFLAG = True

motd = '\n\n~*~ ~*~ NZBMegasearcH detached trend ~*~ ~*~'
print motd

#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ 
cfg,cgen = config_settings.read_conf()
logsdir = SearchModule.resource_path('logs/')
logging.basicConfig(filename=logsdir+'nzbmegasearch_detachedtrend.log',level=logging.INFO,format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
log = logging.getLogger(__name__)
handler = logging.handlers.RotatingFileHandler(logsdir+'nzbmegasearch_detachedtrend.log', maxBytes=cgen['log_size'], backupCount=cgen['log_backupcount'])
log.addHandler(handler)
log.info(motd)
sugg = SuggestionResponses(cfg, cgen)
#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ 

def pollsuggestions():
	sugg.asktrend_allparallel()
	sugg.asktrend_saveondisk()
	
#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ 
print '>> Waiting default: ' + str(cgen['trends_refreshrate'])

while 1:	
	pollsuggestions()
	if(len(sugg.movie_trend) == 0 or  len(sugg.show_trend) == 0):
		print datetime.datetime.now().strftime("%Y-%m-%d %H:%M") + ' Error retreiving trends. Waiting 5s and retrying'
		log.info(' Error retreiving trends. Waiting 5s and retrying')
		time.sleep(5)
	else: 
		time.sleep(cgen['trends_refreshrate'])
		
	

