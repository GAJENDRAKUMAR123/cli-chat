# chat_server_mongodb.py
# This server relays messages to all clients and saves chat history to MongoDB.

import socket
import threading
from pymongo import MongoClient
from datetime import datetime

# --- Configuration ---
HOST = '0.0.0.0'
PORT = 65432

# --- MongoDB Configuration ---
# Make sure you have a MongoDB server running on localhost
try:
    MONGO_CLIENT = MongoClient('mongodb://localhost:27017/')
    DB = MONGO_CLIENT['chat_application']
    CHAT_COLLECTION = DB['chat_history']
    print("[DATABASE] Connected to MongoDB successfully.")
except Exception as e:
    print(f"[DATABASE ERROR] Could not connect to MongoDB: {e}")
    print("Please ensure MongoDB is running.")
    exit()

# --- State ---
# Dictionary to hold client sockets and their names
clients = {}
clients_lock = threading.Lock()

# --- Functions ---
def broadcast(message, sender_conn):
    """
    Sends a message to every client except the one who sent it.
    """
    with clients_lock:
        for client_conn in clients:
            if client_conn != sender_conn:
                try:
                    client_conn.send(message)
                except socket.error:
                    print(f"Failed to send message to a client. Removing.")
                    # Removal will be handled in the main client loop upon disconnect

def save_message(name, message_text):
    """
    Saves a message document to the MongoDB collection.
    """
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
    """
    Handles a single client connection.
    """
    ip, port = addr
    name = None
    try:
        # The first message from the client is their name
        name = conn.recv(1024).decode('utf-8')
        if not name:
            raise ConnectionError("Client did not provide a name.")

        print(f"[NEW CONNECTION] {name} ({ip}:{port}) connected.")
        
        with clients_lock:
            clients[conn] = name
        
        # Announce the new user to everyone else
        announcement = f"[SERVER] {name} has joined the chat.".encode('utf-8')
        broadcast(announcement, conn)

        while True:
            message = conn.recv(1024)
            if not message:
                break # Client disconnected

            decoded_message = message.decode('utf-8')
            
            # Save the message to the database
            save_message(name, decoded_message)

            # Create the message format for broadcasting
            broadcast_message = f"[{name}]: ".encode('utf-8') + message
            print(f"Broadcasting from {name}: {decoded_message}")
            
            # Broadcast to all other clients
            broadcast(broadcast_message, conn)

    except (ConnectionResetError, ConnectionError):
        # Handle client disconnect
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
    """
    Starts the main chat server.
    """
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
