import flask
from flask import jsonify, request
from functools import wraps
'''
Application: Booking of Meeting Rooms
Brief context: Basically we can check meeting rooms, book meeting rooms, remove meeting room bookings, add participants into a meeting room, remove participants from a meeting room
_______________________________________________________________________________
Nouns: /meeting_rooms_available, /meeting_room
Different API calls:
GET /meeting_rooms_available
GET /meeting_rooms_available?id=1
PUT /meeting_rooms_available?id=1 {'request': 'book'} Authorization: Basic YWRtaW46c2VjcmV0
PUT /meeting_rooms_available?id=1 {'request': 'delete'} Authorization: Basic YWRtaW46c2VjcmV0
GET /meeting_room?id=1
POST /meeting_room?id=1 {"participants": ["Tom", "Jerry"]} Authorization: Basic YWRtaW46c2VjcmV0
DELETE /meeting_room?id=1 {"participants": ["Tom"]} Authorization: Basic YWRtaW46c2VjcmV0

_______________________________________________________________________________
For simple storage, there are 2 containers to store information, namely
meeting_rooms_status - for simple access and store the availability of the rooms - a counter to show the number of rooms available, and also the status of the rooms
meeting_rooms - to retrieve more detailed information about a particular room - max participants of room, current count of participants, all participants
_______________________________________________________________________________
Implementation details:
GET /
Shows the available HTTP commands, resources and examples - more of a documentation kind of thing

GET /meeting_rooms_available
returns the number of meeting rooms available and available rooms (rooms with open status)

GET /meeting_rooms_available?id=1
returns the status of that chosen room (either 'open' or 'booked')

PUT /meeting_rooms_available?id=1 {'request': 'book'} Authorization: Basic YWRtaW46c2VjcmV0
Authentication will be required - username(admin) & password(1234)
This will basically change the status of that meeting room from 'open' to 'booked'
and reduces the available meeting rooms count by 1

PUT /meeting_rooms_available?id=1 {'request': 'delete'} Authorization: Basic YWRtaW46c2VjcmV0
This will basically change the status of that meeting room from 'booked' to 'open'
and increases the available meeting rooms count by 1
this will also go to that particular meeting room to empty the participants and reset count to 0 (back to default)

GET /meeting_room?id=1
returns detailed information about a particular room - max participants of room, current count of participants, all participants

POST /meeting_room?id=1 {"participants": ["Tom", "Jerry"]} Authorization: Basic YWRtaW46c2VjcmV0
This will add the participants included in the request body into the meeting room
the count of participants will also be increased with each participant added into the room
However if the participant count exceeeds the maximum capacity of the room, 
it will return error with message that it has exceeded the max capacity

DELETE /meeting_room?id=1 {"participants": ["Tom"]} Authorization: Basic YWRtaW46c2VjcmV0
This will delete the participants included in the request body into the meeting room
the count of participants will also be decreased with each participant added into the room
'''

app = flask.Flask(__name__)  # Creates Flask application object
app.config["DEBUG"] = True  # Will display error if there is

# Variables to hold data of Meeting Rooms Status & Meeting Rooms
meeting_rooms_status = {
    'availability': 3,
    'rooms': {
        '1': {'status': 'open'},
        '2': {'status': 'open'},
        '3': {'status': 'open'},
    }
}

meeting_rooms = {
    '1': {
        'id': 1,
        'max_capacity': 15,
        'current_count': 0,
        'participants': []
        },
    '2': {
        'id': 2,
        'max_capacity': 5,
        'current_count': 0,
        'participants': []
        },
    '3': {
        'id': 3,
        'max_capacity': 3,
        'current_count': 0,
        'participants': []
        }
}

'''
Basic HTTP Authorisation
Usage:
Use @requires_auth decorator
e.g.
@app.route('/paththatrequiresauth')
@requires_auth
def api_hello():
    return "Auth pass!"
'''
def check_auth(username, password):
    return username == 'admin' and password == 'pw1234'

def authenticate():
    message = {'message': "This requires authorisation. Please enter your username and password"}
    resp = jsonify(message)

    resp.status_code = 401
    resp.headers['WWW-Authenticate'] = 'Basic realm="Example"'

    return resp

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth:
            return authenticate()

        elif not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)

    return decorated


@app.route('/', methods=['GET'])
def home():
    message = {
        'status': 200,
        'message': 'Please check available resources',
        'resources': ['/meeting_rooms_available', '/meeting_room'],
        '/meeting_rooms_available': {
            'methods': ['GET', 'PUT'],
            'params': ['id (optional for GET)'],
            'authorisation': 'username and password required to book and delete meeting rooms',
            'purpose': 'Check meeting rooms statuses, book meeting room, remove meeting room booking',
            'examples': ['GET /meeting_rooms_available', 'GET /meeting_rooms_available?id=2', 'PUT /meeting_rooms_available?id=2 {"request": "book"}', 'PUT /meeting_rooms_available?id=2 {"request": "delete"}']
        },
        '/meeting_room': {
            'methods': ['GET', 'POST', 'DELETE'],
            'params': ['id'],
            'authorisation': 'username and password required to add and delete participants',
            'purpose': 'Check meeting room status, add participants into meeting room, delete participants from meeting room',
            'examples': ['GET /meeting_room?id=2', 'POST /meeting_room?id=2 {"participants": ["John", "Tim"]}', 'DELETE /meeting_room?id=2 {"participants": ["John"]}']
        },

    }
    return jsonify(message)


'''
GET REQUEST
Get the number of meeting rooms available to be booked & the list of them
'''
@app.route('/meeting_rooms_available', methods=['GET'])
def get_available_meeting_rooms():

    # If id is specified, return the status of that particular room
    if 'id' in request.args:  # e.g 127.0.0.1:5000/meeting_rooms_available?id=2
        room_id = str(request.args['id'])
        if room_id not in meeting_rooms_status['rooms'].keys(): return no_specified_room(room_id)
        return meeting_rooms_status['rooms'][room_id]

    # No id specified: return general status
    available_rooms = []
    for room_id, room in meeting_rooms_status['rooms'].items():
        if room['status'] == 'open':
            available_rooms.append(room_id)
    return jsonify({'availability': meeting_rooms_status['availability'], 'available_rooms': available_rooms })

'''
2 PUT REQUEST
1. Book a particular meeting room
2. Delete an existing booking
'''
@app.route('/meeting_rooms_available', methods=['PUT'])
@requires_auth
def book_meeting_room():

    # Handle Inputs
    if 'id' not in request.args: return 'Please specify room id', 404
    room_id = str(request.args['id'])
    if room_id not in meeting_rooms_status['rooms'].keys(): return no_specified_room(room_id)
    if not request.json or not request.json['request'] or request.json['request'] != 'book' and request.json['request'] != 'delete':
        return 'Please input a valid request message', 404

    # To Book a Meeting Room:
    if request.json['request'] == 'book':
        if meeting_rooms_status['rooms'][room_id]['status'] == 'open':
            meeting_rooms_status['rooms'][room_id]['status'] = 'booked'
            meeting_rooms_status['availability'] -= 1
            message = {
                'status': 200,
                'message': 'Room ' + str(room_id) + ' is booked successfully',
                'current_bookings': meeting_rooms_status['rooms']
            }
            return jsonify(message)
        else:
            return 'Room already booked. Please book other available rooms', 404

    # To Delete (or 'unbook') a Meeting Room:
    if request.json['request'] == 'delete':
        if meeting_rooms_status['rooms'][room_id]['status'] == 'booked':
            # Update meeting_rooms_status
            meeting_rooms_status['rooms'][room_id]['status'] = 'open'
            meeting_rooms_status['availability'] += 1

            # meeting_rooms
            meeting_rooms[room_id]['participants'] = []
            meeting_rooms[room_id]['current_count'] = 0

            message = {
                'status': 200,
                'message': 'Room ' + str(room_id) + ' booking is deleted successfully',
                'current_bookings': meeting_rooms_status['rooms']
            }
            return jsonify(message)
        else:
            return 'Room is not already booked. Please check again.', 404


'''
POST REQUEST
Add participants into a meeting room
'''
@app.route('/meeting_room', methods=['POST'])
@requires_auth
def add_participants():

    # Handle Inputs
    if 'id' not in request.args: return 'Please specify room id', 404
    room_id = str(request.args['id'])
    if room_id not in meeting_rooms_status['rooms'].keys(): return no_specified_room(room_id)
    if not request.json or not request.json['participants'] or type(request.json['participants']) != list or len(request.json['participants']) <= 0:
        return 'Please input a valid request message', 404


    # Check if Room is already booked - you cannot add participant into a room that is not booked
    if meeting_rooms_status['rooms'][room_id]['status'] == 'open':
        return 'Room is not booked. Please choose a valid room', 404

    # Add Participant(s)
    for participant in request.json['participants']:
        if meeting_rooms[room_id]['current_count'] >= meeting_rooms[room_id]['max_capacity']:
            return 'Room is full. Cannot add more participants', 404
        meeting_rooms[room_id]['current_count'] += 1
        meeting_rooms[room_id]['participants'].append(participant)

    message = {
        'status': 200,
        'message': 'Participants added into room ' + str(room_id),
        'statusOfRoom': meeting_rooms[room_id]
    }
    return jsonify(message)

'''
DELETE REQUEST
Remove participants from a meeting room
'''
@app.route('/meeting_room', methods=['DELETE'])
@requires_auth
def remove_participants():

    # Handle Inputs
    if 'id' not in request.args: return 'Please specify room id', 404
    room_id = str(request.args['id'])
    if room_id not in meeting_rooms_status['rooms'].keys(): return no_specified_room(room_id)
    if not request.json or not request.json['participants'] or type(request.json['participants']) != list or len(request.json['participants']) <= 0:
        return 'Please input a valid request message', 404


    # Check if Room is already booked - you cannot remove participant into a room that is not booked
    if meeting_rooms_status['rooms'][room_id]['status'] == 'open':
        return 'Room is not booked. Please choose a valid room', 404

    # Remove Participant(s)
    removed = []
    for participant in request.json['participants']:
        for p in meeting_rooms[room_id]['participants']:
            if p == participant:
                meeting_rooms[room_id]['participants'].remove(participant)
                removed.append(participant)
                meeting_rooms[room_id]['current_count'] -= 1

    # when not all specified participants are correctly identified
    if len(removed) < len(request.json['participants']):
        message = {
            'status': 200,
            'message': 'Not all participants are removed',
            'removed_participants': removed,
            'statusOfRoom': meeting_rooms[room_id]
        }
        return jsonify(message)

    # All specified participants are removed
    message = {
        'status': 200,
        'message': 'Specified participants are removed' + str(room_id),
        'statusOfRoom': meeting_rooms[room_id]
    }
    return jsonify(message)

'''
GET REQUEST
See meeting room status - participants, etc
'''
@app.route('/meeting_room', methods=['GET'])
def get_meeting_room():

    # Handle Inputs
    if 'id' not in request.args: return 'Please specify room id', 404
    room_id = str(request.args['id'])
    if room_id not in meeting_rooms_status['rooms'].keys(): return no_specified_room(room_id)

    message = {
        'status': 200,
        'statusOfRoom': meeting_rooms[room_id]
    }
    return jsonify(message)



'''
ERROR HANDLES
'''
@app.errorhandler(404)
def no_specified_room(roomid):
    message = {
        'status': 404,
        'message': 'No such room id: ' + roomid,
    }
    resp = jsonify(message)
    resp.status_code = 404
    return resp

@app.errorhandler(404)
def page_not_found(e):
    message = {
        'status': 404,
        'message': 'Not Found: ' + request.url,
    }
    resp = jsonify(message)
    resp.status_code = 404

    return resp

if __name__ == '__main__':
    app.run() # Runs application Server