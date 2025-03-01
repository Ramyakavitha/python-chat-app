# python-chat-app
Chat App with Socket Programming and MySQL in Python
This Chat App is a simple messaging application built using socket programming and MySQL. It allows users to connect to a central server and communicate with each other in real-time. The application is written in Python and utilizes the socket module for network communication and the mysql-connector-python library for interacting with the MySQL database.

Features
Real-time messaging: Users can send and receive messages in real-time.
User registration: New users can register their username and password to access the chat application.
User authentication: Users can log in with their registered username and password to access the chat interface.
User presence tracking: The application shows the online status of users.
Message history: Users can view their chat history, including messages sent and received.
Prerequisites
To run this Chat App, you need to have the following installed:

Python 3
MySQL server
Additionally, you need to install the following Python libraries:

mysql-connector-python
termcolor
You can install these libraries using the following command:

bash
Copy
pip install mysql-connector-python termcolor
Setup and Configuration
Clone this repository to your local machine:
bash
Copy
git clone https://github.com/your-username/chat-app.git
Create a MySQL database to store user information and chat history.
bash
Copy
mysql -u <username> -p
sql
Copy
CREATE DATABASE chat_app;
USE chat_app;
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) NOT NULL,
    password VARCHAR(255) NOT NULL
);
CREATE TABLE messages (
    id INT AUTO_INCREMENT PRIMARY KEY,
    sender VARCHAR(255) NOT NULL,
    receiver VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
Update the database connection details in the config.py file.
python
Copy
DB_HOST = 'localhost'
DB_USER = 'your-username'
DB_PASSWORD = 'your-password'
DB_DATABASE = 'chat_app'
Usage
Start the server by running the following command:
bash
Copy
python server.py
Users can connect to the server using a client by running the following command:
bash
Copy
python client.py
Users will be prompted to register or log in using their username and password.

Once logged in, users can start sending and receiving messages in real-time.

Users can type !exit to log out and exit the chat application.



