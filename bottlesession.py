#!/usr/bin/env python
#
#  Bottle session manager.  See README for full documentation.
#
#  Written by: Sean Reifschneider <jafo@tummy.com>

from __future__ import with_statement

import bottle


def authenticator(session_manager, login_url = '/auth/login'):
	'''Create an authenticator decorator.

	:param session_manager: A session manager class to be used for storing
			and retrieving session data.  Probably based on :class:`BaseSession`.
	:param login_url: The URL to redirect to if a login is required.
			(default: ``'/auth/login'``).
	'''
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
							bottle.request.fullpath, path = '/',
							expires = 3600)
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
	'''Base class which implements some of the basic functionality required for
	session managers.  Cannot be used directly.

	:param cookie_expires: Expiration time of session ID cookie, either `None`
			if the cookie is not to expire, a number of seconds in the future,
			or a datetime object.  (default: 30 days)
	'''
	def __init__(self, cookie_expires = 86400*30):
		self.cookie_expires = cookie_expires

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
					path = '/', expires = self.cookie_expires)

		#  load existing or create new session
		data = self.load(sessionid)
		if not data:
			data = { 'sessionid' : sessionid, 'valid' : False }
			self.save(data)

		return data


class PickleSession(BaseSession):
	'''Class which stores session information in the file-system.

	:param session_dir: Directory that session information is stored in.
			(default: ``'/tmp'``).
	'''
	def __init__(self, session_dir = '/tmp', *args, **kwargs):
		super(BaseSession, self).__init__(*args, **kwargs)
		self.session_dir = session_dir

	def load(self, sessionid):
		filename = os.path.join(self.session_dir, 'session-%s' % sessionid)
		if not os.path.exists(filename): return None
		with open(filename, 'r') as fp: session = pickle.load(fp)
		return session

	def save(self, data):
		sessionid = data['sessionid']
		fileName = os.path.join(self.session_dir, 'session-%s' % sessionid)
		tmpName = fileName + '.' + str(uuid.uuid4())
		with open(tmpName, 'w') as fp: self.session = pickle.dump(data, fp)
		os.rename(tmpName, fileName)
