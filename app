#!/usr/bin/env python

from bottle import route, view
import bottle, bottlesession


####################
#session_manager = bottlesession.PickleSession()
session_manager = bottlesession.CookieSession()
valid_user = bottlesession.authenticator(session_manager)

@route('/')
@route('/:name')
@valid_user()
def hello(name = 'world'):
	return '<h1>Hello %s!</h1>' % name.title()

@route('/auth/login')
def login():
	session = session_manager.get_session()
	session['valid'] = True
	session_manager.save(session)
	bottle.redirect(bottle.request.get_cookie('validuserloginredirect', '/'))


##################
app = bottle.app()
if __name__ == '__main__':
	bottle.debug(True)
	bottle.run(app = app)
