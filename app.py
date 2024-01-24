from flask import Flask, jsonify, request
from flask_cors import CORS
import mysql.connector
from mysql.connector import Error
from datetime import datetime, timedelta

app = Flask(__name__)
CORS(app)

hostname = "4rl.h.filess.io"
database = "sampledb_battleland"
port = "3307"
username = "sampledb_battleland"
password = "d41fc9d600798d0566c85dcc6d62f6096e8b41d5"

def connect_to_database():
    try:
        connection = mysql.connector.connect(host=hostname, database=database, user=username, password=password, port=port)
        if connection.is_connected():
            return connection
    except Error as e:
        print("Error while connecting to MySQL", e)
        return None

def get_current_week_start():
    # today = datetime.now()
    # return today - timedelta(days=today.weekday())
    today = datetime.now()
    # Extract the date portion without the time
    current_week_start = today - timedelta(days=today.weekday())
    current_week_start = current_week_start.date()
    return current_week_start

@app.route('/api/current-week-leaderboard', methods=['GET'])
def current_week_leaderboard():
    connection = connect_to_database()
    if connection:
        try:
            cursor = connection.cursor()
            current_week_start = get_current_week_start()
            print("current week=")
            print(current_week_start)
            query = f"SELECT * FROM score_table WHERE TimeStamp >= '{current_week_start}' ORDER BY Score DESC LIMIT 200;"
            cursor.execute(query)
            result = cursor.fetchall()
            leaderboard = [{'UID': row[0], 'Name': row[1], 'Score': row[2], 'Country': row[3], 'TimeStamp': row[4]} for row in result]
            return jsonify({'leaderboard': leaderboard})
        except Error as e:
            print("Error executing SQL query", e)
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

@app.route('/api/last-week-leaderboard/<country>', methods=['GET'])
def last_week_leaderboard(country):
    # country = request.args.get('country')
    if not country:
        return jsonify({'error': 'Country parameter is required'}), 400

    connection = connect_to_database()
    if connection:
        try:
            cursor = connection.cursor()
            current_week_start = get_current_week_start()
            last_week_start = current_week_start - timedelta(days=7)
            print("current week start--=")
            print(current_week_start)
            print("\n")
            print("last week start=")
            print(last_week_start)
            query = f"SELECT * FROM score_table WHERE TimeStamp >= '{last_week_start}' AND TimeStamp < '{current_week_start}' AND Country = '{country}' ORDER BY Score DESC LIMIT 200;"
            cursor.execute(query)
            result = cursor.fetchall()
            leaderboard = [{'UID': row[0], 'Name': row[1], 'Score': row[2], 'Country': row[3], 'TimeStamp': row[4]} for row in result]
            return jsonify({'leaderboard': leaderboard})
        except Error as e:
            print("Error executing SQL query", e)
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

@app.route('/api/user-rank/<user_id>', methods=['GET'])
def user_rank(user_id):
    # user_id = request.args('userId')
    # connection.query(SELECT COUNT(*) as rank FROM scores WHERE Score > (SELECT Score FROM scores WHERE UID = ?), [req.params.userId], (error, results) =>
    print(user_id)
    if not user_id:
        return jsonify({'error': 'userId parameter is required'}), 400

    connection = connect_to_database()
    if connection:
        try:
            print("inside try block")
            cursor = connection.cursor()
            query = f"SELECT t.Rank FROM (SELECT UID, RANK() OVER (ORDER BY Score DESC) as 'Rank' FROM score_table) t WHERE t.UID = '{user_id}';"
            cursor.execute(query)
            result = cursor.fetchone()
            if result:
                return jsonify({'userRank': result[0]})
            else:
                return jsonify({'error': 'User not found'}), 404
        except Error as e:
            print("Error executing SQL query", e)
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
# @app.route('/userRank/<int:userId>', methods=['GET'])
# def get_user_rank(userId):
#     cur = mysql.connection.cursor()
#     cur.execute("""
#         SELECT COUNT(*) as rank
#         FROM scores
#         WHERE Score > (
#             SELECT Score
#             FROM scores
#             WHERE UID = %s
#         )
#     """, [userId])
#     result = cur.fetchone()
#     rank = result['rank'] + 1
#     return jsonify({'rank': rank})

if __name__ == '__main__':
    # app.run(debug=True)
    app.run(debug=True, use_reloader=False)
    print(app.url_map)

