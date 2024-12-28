import mysql.connector

class Database:
    def __init__(self):
        print("Database created")
        self.connection = mysql.connector.connect(
            host="127.0.0.1",
            port=3306,
            user="root",
            password="",
            database="kavin_attendee"
        )
        
        # check if the connection is successful
        if self.connection.is_connected():
            print("Database connection successful")
        else:
            print("Database connection failed")

        self.cursor = self.connection.cursor()
        

    def create_database(self):
        self.cursor.execute("CREATE DATABASE IF NOT EXISTS attendee")
        self.connection.commit()

    def insert(self, userId, name, time, percentage, image, sent_to_server, server_response, type, sent_to_server_time):
        query = "INSERT INTO attendees (user_id, name, time, percentage, image, sent_to_server, server_response, type, sent_to_server_time) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
        values = (userId, name, time, percentage, image, sent_to_server, server_response, type, sent_to_server_time)
        self.cursor.execute(query, values)
        self.connection.commit()

    def get_all(self):
        self.cursor.execute("SELECT * FROM attendees")
        return self.cursor.fetchall()

    def get_all_unsent(self):
        self.cursor.execute("SELECT * FROM attendees WHERE sent_to_server = 0")
        return self.cursor.fetchall()

    def update_sent(self, id):
        self.delete(id)

    def delete(self, id):
        query = "DELETE FROM attendees WHERE id = %s"
        self.cursor.execute(query, (id,))
        self.connection.commit()

    def close(self):
        if hasattr(self, 'cursor') and self.cursor:
            try:
                self.cursor.close()
            except ReferenceError:
                pass
        if hasattr(self, 'connection') and self.connection:
            try:
                self.connection.close()
            except ReferenceError:
                pass

    def __del__(self):
        self.close()
    
    def update_server_response(self, id, response, sent_to_server_time):
        query = "UPDATE attendees SET server_response = %s, sent_to_server_time = %s, sent_to_server = 0 WHERE id = %s"
        self.cursor.execute(query, (response, sent_to_server_time, id))
        self.connection.commit()