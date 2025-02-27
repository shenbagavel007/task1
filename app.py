from flask import Flask, request, jsonify
from flask_mysqldb import MySQL
from datetime import datetime
import threading
import time

app = Flask(__name__)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'  
app.config['MYSQL_PASSWORD'] = 'mypassword'  
app.config['MYSQL_DB'] = 'message_scheduler'

mysql = MySQL(app)

def send_message(message_id):
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("UPDATE messages SET status = 'sent' WHERE id = %s", (message_id,))
        mysql.connection.commit()
        cursor.close()
    except Exception as e:
        print(f"Error sending message {message_id}: {e}")

def check_scheduled_messages():
    while True:
        try:
            cursor = mysql.connection.cursor()
            cursor.execute("SELECT id, scheduled_time FROM messages WHERE status = 'pending'")
            messages = cursor.fetchall()

            current_time = datetime.now()

            for message in messages:
                message_id, scheduled_time = message
                if scheduled_time <= current_time:
                    send_message(message_id)

            time.sleep(60)  
        except Exception as e:
            print(f"Error checking scheduled messages: {e}")
            time.sleep(60) 

thread = threading.Thread(target=check_scheduled_messages)
thread.daemon = True
thread.start()

@app.route('/schedule_message', methods=['POST'])
def schedule_message():
    try:
        data = request.get_json()
        recipient_number = data['recipient_number']
        message = data['message']
        scheduled_time = datetime.strptime(data['scheduled_time'], '%Y-%m-%d %H:%M:%S')

        cursor = mysql.connection.cursor()
        cursor.execute("INSERT INTO messages (recipient_number, message, scheduled_time, status) VALUES (%s, %s, %s, %s)",
                       (recipient_number, message, scheduled_time, 'pending'))
        mysql.connection.commit()
        cursor.close()

        return jsonify({"message": "Message scheduled successfully!"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route('/messages', methods=['GET'])
def get_messages():
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT id, recipient_number, message, scheduled_time, status FROM messages")
        messages = cursor.fetchall()
        cursor.close()

        result = []
        for message in messages:
            result.append({
                "id": message[0],
                "recipient_number": message[1],
                "message": message[2],
                "scheduled_time": message[3].strftime('%Y-%m-%d %H:%M:%S'),
                "status": message[4]
            })

        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route('/messages/<int:id>', methods=['DELETE'])
def cancel_message(id):
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT status FROM messages WHERE id = %s", (id,))
        message = cursor.fetchone()

        if not message:
            return jsonify({"error": "Message not found!"}), 404

        if message[0] == 'sent':
            return jsonify({"error": "Cannot cancel a sent message!"}), 400

        cursor.execute("DELETE FROM messages WHERE id = %s", (id,))
        mysql.connection.commit()
        cursor.close()

        return jsonify({"message": "Message canceled successfully!"}), 204
    except Exception as e:
        return jsonify({"error": str(e)}), 400


if __name__ == '__main__':
    app.run(debug=True)