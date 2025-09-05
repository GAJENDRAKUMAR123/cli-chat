# chat_server_docker.py
# This server relays messages and saves chat history to a MongoDB container.

import socket
import threading
from pymongo import MongoClient
from datetime import datetime
import time
import os

# --- Configuration ---
HOST = '0.0.0.0'
PORT = 65432

MONGO_URI = os.environ.get('MONGO_DATABASE_URI', None)
# MONGO_URI = os.environ.get('MONGO_DATABASE_URI', 'mongodb://localhost:27017/chat_application')
MONGO_CLIENT = None
DB = None
CHAT_COLLECTION = None

def connect_to_mongo():
    """Tries to connect to MongoDB using the URI, retrying if it fails."""
    global MONGO_CLIENT, DB, CHAT_COLLECTION
    retries = 10
    for i in range(retries):
        try:
            # Use the MONGO_URI variable to connect
            MONGO_CLIENT = MongoClient(MONGO_URI)
            DB = MONGO_CLIENT['chat_application']
            CHAT_COLLECTION = DB['chat_history']
            # The ismaster command is cheap and does not require auth.
            MONGO_CLIENT.admin.command('ismaster')
            print("[DATABASE] Connected to MongoDB successfully.")
            return True
        except Exception as e:
            print(f"[DATABASE ERROR] Could not connect to MongoDB: {e}. Retrying in 5 seconds...")
            time.sleep(5)
    print("[DATABASE ERROR] Could not connect to MongoDB after several retries. Exiting.")
    return False

# --- State ---
clients = {}
clients_lock = threading.Lock()

# --- Functions ---
def broadcast(message, sender_conn):
    with clients_lock:
        for client_conn in clients:
            if client_conn != sender_conn:
                try:
                    client_conn.send(message)
                except socket.error:
                    print("Failed to send message to a client.")

def save_message(name, message_text):
    if not CHAT_COLLECTION:
        print("[DATABASE ERROR] Not connected to DB. Cannot save message.")
        return
    try:
        message_document = {
            "sender_name": name,
            "message": message_text,
            "timestamp": datetime.utcnow()
        }
        CHAT_COLLECTION.insert_one(message_document)
    except Exception as e:
        print(f"[DATABASE ERROR] Could not save message to MongoDB: {e}")

def handle_client(conn, addr):
    ip, port = addr
    name = None
    try:
        name = conn.recv(1024).decode('utf-8')
        if not name:
            raise ConnectionError("Client did not provide a name.")

        print(f"[NEW CONNECTION] {name} ({ip}:{port}) connected.")
        
        with clients_lock:
            clients[conn] = name
        
        announcement = f"[SERVER] {name} has joined the chat.".encode('utf-8')
        broadcast(announcement, conn)

        while True:
            message = conn.recv(1024)
            if not message:
                break

            decoded_message = message.decode('utf-8')
            save_message(name, decoded_message)
            broadcast_message = f"[{name}]: ".encode('utf-8') + message
            print(f"Broadcasting from {name}: {decoded_message}")
            broadcast(broadcast_message, conn)

    except (ConnectionResetError, ConnectionError):
        pass
    finally:
        with clients_lock:
            if conn in clients:
                name = clients.pop(conn)
                departure_message = f"[SERVER] {name} has left the chat.".encode('utf-8')
                broadcast(departure_message, None)
                print(f"[DISCONNECTED] {name} ({ip}:{port}) disconnected.")
        conn.close()

def start_server():
    if not connect_to_mongo():
        return

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()
    print(f"[LISTENING] Server is listening on {HOST}:{PORT}")

    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()

if __name__ == "__main__":
    start_server()
