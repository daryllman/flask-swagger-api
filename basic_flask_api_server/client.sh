# Booking of Meeting Rooms
# Context: Basically we can check meeting rooms, book meeting rooms, remove meeting room bookings, add participants into a meeting room, remove participants from a meeting room

# For the below commands, I have created them in a logical order to test the functionality and workability of them
# It will go like this:
# 0. Shows the available commands
# 1. Check meeting rooms available - all should be 'open'
# 2. Book meeting room 1
# 3. Check meeting rooms available - availability will be decreased, and room 1 will be booked
# 4. Check status of meeting room 1 - should be 'booked'
# 5. Remove booking of meeting room 1
# 6. Check status of meeting room 1 again - should be 'open'
# 7. Book meeting room 2
# 8. Add participants into meeting room 2 - Tom & Jerry
# 9. Check the info of meeting room 2 - should show Tom & Jerry exist, and other info
# 10. Remove a participant - Tom
# 11. Check the info of meeting room 2 again - should be updated
# 12. Remove booking of meeting room 2
# 13. Check the info of meeting room 2 - should be empty
# 14. Check meeting rooms available - should be default state as there are no more bookings

echo
echo "____________________________"
echo "GET /"
echo "purpose: Shows the available HTTP commands and examples"
curl  http://localhost:5000/
echo "____________________________"
echo "____________________________"



echo "____________________________"
echo "GET /meeting_rooms_available"
echo "purpose: Check meeting rooms available"
curl  http://localhost:5000/meeting_rooms_available

echo "____________________________"
echo "PUT /meeting_rooms_available?id=1 {'request': 'book'} Authorization: Basic YWRtaW46c2VjcmV0"
echo "purpose: Book a meeting room (room 1)"
curl -H "Content-type: application/json" -u "admin:pw1234" -X PUT http://localhost:5000/meeting_rooms_available?id=1 -d '{"request": "book"}'

echo "____________________________"
echo "GET /meeting_rooms_available"
echo "purpose: Check meeting rooms available"
curl  http://localhost:5000/meeting_rooms_available

echo "____________________________"
echo "GET /meeting_rooms_available?id=1"
echo "purpose: Check status of a particular meeting room (room 1)"
curl  http://localhost:5000/meeting_rooms_available?id=1

echo "____________________________"
echo "PUT /meeting_rooms_available?id=1 {'request': 'delete'} Authorization: Basic YWRtaW46c2VjcmV0"
echo "purpose: Remove booking of a meeting room (room 1)"
curl -H "Content-type: application/json" -u "admin:pw1234" -X PUT http://localhost:5000/meeting_rooms_available?id=1 -d '{"request": "delete"}'

echo "____________________________"
echo "GET /meeting_rooms_available?id=1"
echo "purpose: Check status of a particular meeting room (room 1)"
curl  http://localhost:5000/meeting_rooms_available?id=1

echo "____________________________"
echo "PUT /meeting_rooms_available?id=2 {'request': 'book'} Authorization: Basic YWRtaW46c2VjcmV0"
echo "purpose: Book a meeting room (room 2)"
curl -H "Content-type: application/json" -u "admin:pw1234" -X PUT http://localhost:5000/meeting_rooms_available?id=2 -d '{"request": "book"}'

echo "____________________________"
echo 'POST /meeting_room?id=2 {"participants": ["Tom", "Jerry"]} Authorization: Basic YWRtaW46c2VjcmV0'
echo "purpose: Add participants into a meeting room (room 2)"
curl -H "Content-type: application/json" -u "admin:pw1234" -X POST http://localhost:5000/meeting_room?id=2 -d '{"participants": ["Tom", "Jerry"]}'

echo "____________________________"
echo "GET /meeting_room?id=2"
echo "purpose: Check a particular meeting room (room 2)"
curl http://localhost:5000/meeting_room?id=2

echo "____________________________"
echo 'DELETE /meeting_room?id=2 {"participants": ["Tom"]} Authorization: Basic YWRtaW46c2VjcmV0'
echo "purpose: Remove participants from a meeting room (room 2)"
curl -H "Content-type: application/json" -u "admin:pw1234" -X DELETE http://localhost:5000/meeting_room?id=2 -d '{"participants": ["Tom"]}'

echo "____________________________"
echo "GET /meeting_room?id=2"
echo "purpose: Check a particular meeting room (room 2)"
curl http://localhost:5000/meeting_room?id=2

echo "____________________________"
echo "PUT /meeting_rooms_available?id=2 Authorization: Basic YWRtaW46c2VjcmV0"
echo "purpose: Remove booking of a meeting room (room 2)"
curl -H "Content-type: application/json" -u "admin:pw1234" -X PUT http://localhost:5000/meeting_rooms_available?id=2 -d '{"request": "delete"}'

echo "____________________________"
echo "GET /meeting_room?id=2"
echo "purpose: Check a particular meeting room (room 2)"
curl http://localhost:5000/meeting_room?id=2

echo "____________________________"
echo "GET /meeting_rooms_available"
echo "purpose: Check meeting rooms available"
curl  http://localhost:5000/meeting_rooms_available




