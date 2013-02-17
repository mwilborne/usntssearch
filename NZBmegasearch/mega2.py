# # ## # ## # ## # ## # ## # ## # ## # ## # ## # ## # ## # ## # ## # ## #    
#~ This file is part of NZBmegasearch by pillone.
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
from flask import request, Response
import SearchModule
import megasearch
import config_settings
from ApiModule import ApiResponses
import miscdefs

#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ 

app = Flask(__name__)
SearchModule.loadSearchModules()
cfg,cgen = config_settings.read_conf()

#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ 
#~ versioning check
ver_notify= { 'chk':0, 
			  'curver': '0.251exp'}

print '~*~ ~*~ NZBMegasearcH (v. '+ str(ver_notify['curver']) + ') ~*~ ~*~'
	
#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ 

@app.route('/s', methods=['GET'])
def search():
	return megasearch.dosearch(request.args, cfg, ver_notify)
			
@app.route('/', methods=['GET','POST'])
def main_index():
	return megasearch.dosearch('', cfg, ver_notify)


@app.route('/api', methods=['GET'])
def api():
	#~ print request.args
	api = ApiResponses(cfg, ver_notify)
	return api.dosearch(request.args)

@app.route('/connect', methods=['GET'])
def connect():
	return miscdefs.connectinfo()
 
  
@app.errorhandler(404)
def generic_error(error):
	return main_index()
