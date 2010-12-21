#!/usr/bin/env python

from bottle import route, view
import bottle, bottlelogin


####################
session_manager = bottlelogin.PickleSession()
valid_user = bottlelogin.authenticator(session_manager)

@route('/')
@route('/:name')
@valid_user()
def hello(name = 'world'):
	return '<h1>Hello %s!</h1>' % name.title()

@route('/auth/login')
def login():
	session = session_manager.get_session()
	session['name'] = 'foo'
	session['valid'] = True
	session_manager.save(session)
	bottle.redirect(bottle.request.COOKIES.get('validuserloginredirect', '/'))


##################
app = bottle.app()
if __name__ == '__main__':
	bottle.debug(True)
	bottle.run(app = app)
