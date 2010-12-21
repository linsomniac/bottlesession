#!/usr/bin/env python

import bottle


def authenticator(session_manager, login_url = '/auth/login'):
	def valid_user(login_url = login_url):
		def decorator(handler, *a, **ka):
			import functools
			@functools.wraps(handler)
			def check_auth(*a, **ka):
				try:
					data = session_manager.get_session()
					if not data['valid']: raise KeyError('Invalid login')
				except (KeyError, TypeError):
					bottle.response.set_cookie('validuserloginredirect',
							bottle.request.fullpath, path = '/', expires = 900)
					bottle.redirect(login_url)

				#  set environment
				if data.get('name'):
					bottle.request.environ['REMOTE_USER'] = data['name']

				return handler(*a, **ka)
			return check_auth
		return decorator
	return(valid_user)


import pickle, os, uuid
class BaseSession:
	def load(self, sessionid):
		raise NotImplementedError

	def save(self, sessionid, data):
		raise NotImplementedError

	def make_session_id(self):
		return str(uuid.uuid4())

	def allocate_new_session_id(self):
		#  retry allocating a unique sessionid
		for i in xrange(100):
			sessionid = self.make_session_id()
			if not self.load(sessionid): return sessionid
		raise ValueError('Unable to allocate unique session')

	def get_session(self):
		#  get existing or create new session identifier
		sessionid = bottle.request.COOKIES.get('sessionid')
		if not sessionid:
			sessionid = self.allocate_new_session_id()
			bottle.response.set_cookie('sessionid', sessionid,
					path = '/', expires = 900)

		#  load existing or create new session
		data = self.load(sessionid)
		if not data:
			data = { 'sessionid' : sessionid, 'valid' : False }
			self.save(data)

		return data


class PickleSession(BaseSession):
	def __init__(self, session_dir = '/tmp'):
		self.session_dir = session_dir

	def load(self, sessionid):
		filename = os.path.join(self.session_dir, 'session-%s' % sessionid)
		if not os.path.exists(filename): return None

		fp = open(filename, 'r')
		session = pickle.load(fp)
		fp.close()
		return session

	def save(self, data):
		sessionid = data['sessionid']
		fileName = os.path.join(self.session_dir, 'session-%s' % sessionid)
		tmpName = fileName + '.' + str(uuid.uuid4())
		fp = open(tmpName, 'w')
		self.session = pickle.dump(data, fp)
		fp.close()
		os.rename(tmpName, fileName)
