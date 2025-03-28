# task1
Instruction:
1.step : first creat vritual environment and install Flask , mysql-connector-python ,Flask-MySQLdb,
2 step : then set up the database connection with your host, userid, password and database name,
How to Run :
1."python app.py" in terminal 
2. then open command prompt and type this to check the POST method
"curl -X POST http://127.0.0.1:5000/schedule_message -H "Content-Type: application/json" -d '{"recipient_number": "1234567890", "message": "Test Message", "scheduled_time": "2025-02-27 15:30:00"}'" (with parameter)\
3. for GET
curl -X GET http://127.0.0.1:5000/messages
4. for Delete
curl -X DELETE http://127.0.0.1:5000/messages/1
this last number 1 is (id) 




