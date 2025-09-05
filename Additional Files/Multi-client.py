# chat_server_broadcast.py
# This server relays messages from any client to all other connected clients.

import socket
import threading

# --- Configuration ---
HOST = '0.0.0.0'
PORT = 65432

# --- State ---
# List to hold all connected client sockets
clients = []
# A lock to ensure thread-safe access to the clients list
clients_lock = threading.Lock()

# --- Functions ---
def broadcast(message, sender_conn):
    """
    Sends a message to every client except the one who sent it.
    """
    with clients_lock:
        for client_conn in clients:
            # Don't send the message back to the original sender
            if client_conn != sender_conn:
                try:
                    client_conn.send(message)
                except socket.error:
                    # Handle cases where the client might have disconnected abruptly
                    print(f"Failed to send message to a client. Removing.")
                    clients.remove(client_conn)
                    client_conn.close()

def handle_client(conn, addr):
    """
    Handles a single client connection.
    """
    ip, port = addr
    print(f"[NEW CONNECTION] {ip}:{port} connected.")

    with clients_lock:
        clients.append(conn)

    try:
        while True:
            # Wait to receive a message from the client
            message = conn.recv(1024)
            if not message:
                break # Client disconnected

            # Create the message format with the sender's IP
            broadcast_message = f"[{ip}]: ".encode('utf-8') + message
            print(f"Broadcasting from {ip}: {message.decode('utf-8')}")
            
            # Broadcast the message to all other clients
            broadcast(broadcast_message, conn)

    except ConnectionResetError:
        print(f"[{ip}] Connection was forcibly closed.")
    finally:
        # When the client disconnects, remove them from the list and close connection
        with clients_lock:
            if conn in clients:
                clients.remove(conn)
        conn.close()
        print(f"[DISCONNECTED] {ip}:{port} disconnected.")

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
        # Create and start a new thread for each client that connects
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()

if __name__ == "__main__":
    start_server()
