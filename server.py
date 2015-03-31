import os
import uuid
from flask import Flask, session, render_template, request, redirect, url_for, jsonify
from flask.ext.socketio import SocketIO, emit
import psycopg2
import psycopg2.extras

app = Flask(__name__, static_url_path='')
app.config['SECRET_KEY'] = 'secret!'

socketio = SocketIO(app)

messages = [{'text':'test', 'name':'testName'}]
searchIn = [{ 'text':'searchterm', 'name':'username'}] #This breaks our messages term and it would break our chat and start inserting empty strings 
users = {}
room = []
rooms = ['Spammers', 'Police','NSA'] # these will remain the names we use, but we will just have to translate them into message(_,2,3)
#global List # what is list?

DefultRoom = 'SELECT message, username FROM NSA'
def connectToDB():
  connectionString = 'dbname=chatroom user=postgres password=Razula host=localhost'
  try:
    return psycopg2.connect(connectionString)
  except:
    print("Can't connect to database")

def updateRoster():
    names = []
    for user_id in  users:
        print users[user_id]['username']
        if len(users[user_id]['username'])==0:
            names.append('Anonymous')
        else:
            names.append(users[user_id]['username'])
    print 'broadcasting names'
    emit('roster', names, broadcast=True)
    
def updateRooms():
    conn = connectToDB()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)      
    query = "select tableName from names"
    cur.execute(query)
    rooms=[]
    room = cur.fetchall()
    for roomNum in room:
        rooms.append(roomNum['tableName'])
        print roomNum['tableName']
    emit('rooms', rooms)
    
    

    
#@app.route('/new_room', methods=['POST'])
@socketio.on('new_room', namespace = '/chat')
def new_room(Pass_Room):

    print "newroom"
    rooms.append(Pass_Room)
    print 'updating rooms'
    updateRooms()
    print Pass_Room
    conn = connectToDB()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)  
    query = " CREATE TABLE IF NOT EXISTS %s ( id serial, username varchar(30) NOT NULL, message varchar(500) NOT NULL, PRIMARY KEY(id))" % Pass_Room
    cur.execute(query)
    conn.commit() 
    query = "INSERT INTO names (tableName) VALUES (%s)"
    cur.execute(query,(Pass_Room,))
    conn.commit()
    print "after query"
    #updateRooms()

   # return jsonify(success= "ok")
    
@socketio.on('changeRoom',namespace='/chat')
def changeRoom(room_name):
    print "changing ROOOOOOOOM"
    session['currentChatRoom'] = room_name
    conn = connectToDB()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)  
    query = "SELECT message, username from %s" % session['currentChatRoom'] 
    cur.execute(query)    
    messages = cur.fetchall()
    
    for message in messages:
        message = {'text':message['message'],'name':message['username']}
        emit('message', message)    
    print session['currentChatRoom']
    
    
@socketio.on('connect', namespace='/chat')
def test_connect():
   
    session['uuid']=uuid.uuid1()
    session['username']='starter name'
    print 'connected'
    session['currentChatRoom']='NSA'    
    users[session['uuid']]={'username':'New User'}
    if session['uuid'] in users:
        del users[session['uuid']]
    updateRoster()
    updateRooms()
    query = "SELECT message, username FROM %s ORDER by id desc limit 10" % session['currentChatRoom']
    conn = connectToDB()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)  
    cur.execute(query)
    messages = cur.fetchall()

    for message in messages:
        message = {'text':message['message'],'name':message['username']}
        emit('message', message)



                
            
@socketio.on('search', namespace='/chat')
def search(searchterm): 
    print searchterm 
    searchterm = '%' + searchterm + '%'
    print searchterm 
    conn = connectToDB()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    #queryold = "SELECT message, username FROM NSA WHERE message LIKE %s"
    query = "SELECT message, username FROM %s WHERE message LIKE %s" % (session['currentChatRoom'],'%s')
    print cur.mogrify(query, (searchterm,)) 
    cur.execute(query,(searchterm,))
    results = cur.fetchall()
    print results
    res = ['user','Text']
    for r in results:
        emit('search', dict(zip(res,r)))
            
    
  
    
@socketio.on('message', namespace='/chat')
def new_message(message):
    conn = connectToDB()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    print "while true"
    tmp = {'text':message, 'name':users[session['uuid']]['username']}
    messages.append(tmp)
    say = message
    print message
    user = session['username']
    #print cur.mogrify("insert into messages (username, message) VALUES (%s,%s)",(user, say))   
    print 'insert'
    conn.commit()
    print say
    query = "INSERT into %s (username, message) VALUES (%s,%s)" % (session['currentChatRoom'],'%s','%s')
    cur.execute(query ,(user, say))
    #print cur.mogrify("insert into messages (username, message) VALUES (%s,%s)",(user, say))        
    #cur.execute("insert into messages (username, message) VALUES (%s,%s)",(user, say))
    print 'insert'
    conn.commit()
    print say
    
    emit('message', tmp, broadcast=True)
    
@socketio.on('identify', namespace='/chat')
def on_identify(message):
    print 'identify' + message
    users[session['uuid']]={'username':message}
    updateRoster()
    updateRooms()


@socketio.on('login', namespace='/chat')
def on_login(pw):
    conn = connectToDB()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    print 'login '  + pw
  
    tmp = {'name':users[session['uuid']]['username']}
    username = users[session['uuid']]['username']
    print username + 'name'
    #currentUser = username
    session['username'] = username
    # the foreign key still gives problems but that is sprint 2, for now we can just have it as is with an id and username and message
    # yea I can see that! cool thanks
    cur.execute("select * from userlist WHERE username = %s AND password = crypt(%s, gen_salt('bf'))",  (username, pw,))
    #cur.execute("select * from userslist WHERE username = %s AND password = %s",  (username, pw,))
    if cur.fetchone():
        return redirect(url_for('index.html'))
    #return app.send_static_file('index.html')
    #users[session['uuid']]={'username':message}
    #updateRoster()
@app.route('/signup',methods=['GET', 'POST'])
#@socketio.on('signup', namespace='/signup', methods=['GET', 'POST'])
def signup():
    
  conn = connectToDB()
  cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)   
  # that should do it least now we can alter the database through python with this in play
  #conn = connectToDB() here we need a connect variable ex(connection ='dbname=reports user=postgres password=fhfh host=localhost')
  #cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
  
  if request.method == 'POST':
      print "HI"
      username = request.form['user']
      print username
      currentUser = username
      session['username'] = username
      print 'Session'
      pw = request.form['pass']
      print pw
      
     #print cur.mognify("insert into userlist (username,password) VALUES (%s,crypt(%s, gen_salt('bf')))",  (username, pw))
      cur.execute("insert into userlist (username,password) VALUES (%s,crypt(%s, gen_salt('bf')))",  (username, pw))
      #cur.execute("insert into userlist (username,password) VALUES (%s,%s)",  (username, pw))
      print 'afterEXCUTE'
      conn.commit()
      print 'comminting'
      print username
      print pw
  return app.send_static_file('signup.html')
    
@socketio.on('disconnect', namespace='/chat')
def on_disconnect():
    #we'll want to drop the current session when they disconnect
    # need a logout button that calls this method
    #session.pop('username',None)
    #the above syntax is the method that is needed to end a session
    session.pop('username',None)
    
    #print 'disconnect'
    #if session['uuid'] in users:
        #del users[session['uuid']]
        #updateRoster()
    return redirect(url_for('mainIndex'))



    


@app.route('/')
def mainIndex():
    conn = connectToDB()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)  
  
    #cur.execute("select * from messages") 
    #rows = cur.fetchall() 
    #for row in rows:
    #    print row
  
    
    
    return app.send_static_file('index.html')
   # return 'Hello World!'

@app.route('/js/<path:path>')
def static_proxy_js(path):
    # send_static_file will guess the correct MIME type
    return app.send_static_file(os.path.join('js', path))
    
@app.route('/css/<path:path>')
def static_proxy_css(path):
    # send_static_file will guess the correct MIME type
    return app.send_static_file(os.path.join('css', path))
    
@app.route('/img/<path:path>')
def static_proxy_img(path):
    # send_static_file will guess the correct MIME type
    return app.send_static_file(os.path.join('img', path))
    
if __name__ == '__main__':
    print "A"

    socketio.run(app, host=os.getenv('IP', '0.0.0.0'), port=int(os.getenv('PORT', 8080)))
     