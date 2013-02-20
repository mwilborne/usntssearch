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
import ConfigParser
from SearchModule import *

# Search on Newznab
class ad_NZBclub(SearchModule):
	# Set up class variables
	def __init__(self, configFile=None):
		super(ad_NZBclub, self).__init__()
		# Parse config file		
		self.name = 'NZBClub'
		self.typesrch = 'CLB'
		self.queryURL = 'https://www.nzbclub.com/nzbfeed.aspx'
		self.baseURL = 'https://www.nzbclub.com'
		self.active = 1
		self.builtin = 1
		self.login = 0
		self.inapi = 1
		
		self.categories = {'Console': {'code':[], 'pretty': 'Console'},
							'Movie' : {'code': [], 'pretty': 'Movie'},
 							'Movie_HD' : {'code': [], 'pretty': 'HD'},
							'Movie_SD' : {'code': [], 'pretty': 'SD'},
							'Audio' : {'code': [], 'pretty': 'Audio'},
							'PC' : {'code': [], 'pretty': 'PC'},
							'TV' : {'code': [], 'pretty': 'TV'},
							'TV_SD' : {'code': [], 'pretty': 'SD'},
							'TV_HD' : {'code': [], 'pretty': 'HD'},
							'XXX' : {'code': [], 'pretty': 'XXX'},
							'Other' : {'code': [], 'pretty': 'Other'},
							'Ebook' : {'code': [], 'pretty': 'Ebook'},
							'Comics' : {'code': [], 'pretty': 'Comics'},
							} 
		self.category_inv= {}
		for key in self.categories.keys():
			prettyval = self.categories[key]['pretty']
			for i in xrange(len(self.categories[key]['code'])):
				val = self.categories[key]['code'][i]
				self.category_inv[str(val)] = prettyval
		
	# Perform a search using the given query string
	def search(self, queryString, cfg):		
		urlParams = dict(q =queryString,
            ig= 1,
            rpp= 200,
            st= 5,
            sp= 1,
            ns= 1	)
         
		parsed_data = self.parse_xmlsearch(urlParams, cfg['timeout'])	
		return parsed_data
