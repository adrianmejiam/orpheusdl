# Wrapper for Qo-DL. Sorrow446.

import os
import time
import json

import requests
from nugspy.exceptions import AuthenticationError, IneligibleError

class Client:
	def __init__(self, **kwargs):
		self.session = requests.Session()
		self.session.headers.update({
			'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; '
				'rv:67.0) Gecko/20100101 Firefox/67.0',
			'Referer': 'https://play.nugs.net/'
		})
		self.base = 'https://streamapi.nugs.net/'

	def fix_json(self, j):
		return json.loads(j.rstrip()[21:-2])
		
	def api_call(self, epoint, method, **kwargs):
		if method == "user.site.login":	
			params={
				'username': kwargs['email'],
				'pw': kwargs['pwd']
			}
		elif method == "user.site.getSubscriberInfo":
			params={}
		elif method == "catalog.container":
			params={
				'containerID': kwargs['id']
			}
		elif not method:
			params={
				'HLS': '1',
				'platformID': kwargs['fmt_id'],
				'trackID': kwargs['id']
			}
		params['orgn'] = "nndesktop"
		params['callback'] = "angular.callbacks._0"
		if method:
			params['method'] = method
		
		r = self.session.get(self.base + epoint, params=params)
		if method == "user.site.login":
			if "USER_NOT_FOUND" in r.text:
				raise AuthenticationError('Invalid credentials.')
		r.raise_for_status()
		return self.fix_json(r.text)

	def auth(self, email, pwd):
		return self.api_call('secureapi.aspx?', 'user.site.login', email=email, pwd=pwd)

	def get_sub_info(self):
		r = self.api_call('secureapi.aspx?', 'user.site.getSubscriberInfo')
		if not r['Response']['subscriptionInfo']['planName']:
			raise IneligibleError("Free accounts are not eligible to download tracks.") 
		return r['Response']['subscriptionInfo']['planName'][9:]

	def get_track_url(self, id, fmt_id):
		r = self.api_call('bigriver/subplayer.aspx?', None, id=id, fmt_id=fmt_id)['streamLink']
		if fmt_id == 4:
			if not "mqa24/" in r:
				self.get_track_url(id, 1)
		return r
	
	def get_album_meta(self, id):
		return self.api_call('api.aspx?', 'catalog.container', id=id)['Response']
