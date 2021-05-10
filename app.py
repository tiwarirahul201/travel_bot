from flask import *
from flask_socketio import *
from demo import Result
import datetime
import random, string




# Init the server
app = Flask(__name__)
app.config['SECRET_KEY'] = 'some super secret key!'
socketio = SocketIO(app, logger=True)

# Send HTML!
@app.route('/')
def root():    
    return render_template('index.html')



# Receive a message from the front end HTML
@socketio.on('send_message')   
def message_recieved(data):
    if 'user_id' not in session:
        x = ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(16))
        print(x)
        session['user_id'] = x

    print(data['text']) # this is from user 
    ans = Result(data['text'])
    emit('message_from_server', {'text':ans}) # we are sending response


if __name__ == '__main__':
    """ Run the app. """    
    socketio.run(app,debug=True)
