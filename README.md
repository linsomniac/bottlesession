Sean Reifschneider <jafo@tummy.com>  
Homepage/Code/bugfixes: [https://github.com/linsomniac/bottlesession](https://github.com/linsomniac/bottlesession)  
License: 3-clause BSD  

BottleSession README
====================

A simple library to make session authenitcation easy with the Bottle
micro-framework.

Features:

   * Saves off URL being hit so that you can redirect after the login.
         (Stored in a cookie)
   * Simple session managers included: store in /tmp and store in cookie.
   * Decorator to specify that a login is required.
   * Saves off login name to "bottle.request.environ['REMOTE_USER']".

Bugs:

   * Could probably stand to have some other session managers.
   * Each request does not re-verify the user, it just checks the session.
         (if the password changes, the session doesn't go invalid)
   * The session data is just a dictionary
         (ideally, there should probably be a "save()" method or
         possibly use the context manager interface?)

Example
-------

See "app", for example:

    #session_manager = PickleSession()
    session_manager = CookieSession()    #  NOTE: you should specify a secret
    valid_user = authenticator(session_manager)

    @route('/')
    @route('/:name')
    @valid_user()
    def hello(name = 'world'):
       return '<h1>Hello %s!</h1>' % name.title()

The "authenticator" creates a decorator that requires authentication.  It
takes a session manager object, see the BaseSession class for the API that
it needs to implement.

"bottlesession" includes a pickle-based session manager that saves session
files in /tmp, much like the stock PHP session store.  See "PickleSession"
in "bottlesession.py" for an example implementation, it's real easy!

"PickleSession()" stores the session in a pickled file under "/tmp" (or other
location, as specified by the "session_dir" argument).  "CookieSession()"
stores the cookie in a secure cookie.  If no cookie is specified, it will
try to generate a hard to guess but persistent secret.  For anything but
trial applications, you should specify a strong secret

You need a login page, valid_user() relies on this being at "/auth/login".
Here is a complete example:

    @route('/auth/login')
    @view('html/login.html')
    def login():
       passwds = { 'guest' : 'guest',}

       username = bottle.request.forms.get('username')
       password = bottle.request.forms.get('password')

       if not username or not password:
          return { 'error' : 'Please specify username and password' }

       session = session_manager.get_session()
       session['valid'] = False

       if password and passwds.get(username) == password:
          session['valid'] = True
          session['name'] = username

       session_manager.save(session)
       if not session['valid']:
          return { 'error' : 'Username or password is invalid' }

       bottle.redirect(bottle.request.COOKIES.get('validuserloginredirect', '/'))

For a logout, just set the session to invalid:

    @route('/auth/logout')
    def logout():
       session = session_manager.get_session()
       session['valid'] = False
       session_manager.save(session)
       bottle.redirect('/auth/login')

And a template for "html/login.html":

    %if error:
       <fieldset><legend>Notice</legend>{{error}}</fieldset>
    %end

    <form method="POST" id="form" action="/auth/login">
       Login name: <input type="text" name="username" /><br/>
       Password: <input type="password" name="password" /><br/>
       <input type="submit" value="Login" name="submit" />
    </form>
