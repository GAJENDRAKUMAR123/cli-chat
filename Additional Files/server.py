# chat_server.py
# This script acts as the server, waiting for a client to connect for a chat.

import socket

# --- Configuration ---
HOST = '0.0.0.0'  # Listen on all network interfaces
PORT = 65432      # Port to listen on

print("--- Chat Server ---")

# Create the main listening socket
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    try:
        s.bind((HOST, PORT))
    except OSError as e:
        print(f"Error binding to port {PORT}: {e}. Is another program using it?")
        exit()

    s.listen()
    print(f"Server is listening for a connection on port {PORT}...")

    # Main loop to accept new connections
    while True:
        print("\nWaiting for a new client to connect...")
        conn, addr = s.accept() # This blocks until a client connects

        with conn:
            print(f"Connected by {addr}. The chat is now live!")
            print("Waiting for the first message from the client...")

            # Chat loop for the connected client
            while True:
                try:
                    # Wait to receive a message from the client
                    client_message = conn.recv(1024).decode('utf-8')
                    if not client_message:
                        print("Client disconnected.")
                        break
                    
                    print(f"Client: {client_message}")

                    # Get a reply from the server user and send it
                    server_reply = input("You: ")
                    conn.sendall(server_reply.encode('utf-8'))

                except ConnectionResetError:
                    print("Connection was forcibly closed by the client.")
                    break
        
        print("Client session ended. Ready to accept a new connection.")
