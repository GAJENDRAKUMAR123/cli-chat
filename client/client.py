import socket
import threading
import os

# --- Configuration ---
# The client will connect to the server using the hostname 'server',
# which is its service name in the docker-compose network.
# A default value is provided for local testing without Docker.
SERVER_HOST = os.environ.get('SERVER_HOST', '127.0.0.1')
SERVER_PORT = 65432
# NAME will be set by user input when the script runs.
NAME = None

def receive_messages(client_socket):
    """Listens for messages from the server and prints them."""
    while True:
        try:
            message = client_socket.recv(1024).decode('utf-8')
            if message:
                # \r moves the cursor to the start of the line.
                # We then print the received message and reprint the user's prompt
                # on a new line, ensuring the user's current input isn't disrupted.
                print(f"\r{message}\n{NAME}: ", end="")
            else:
                # Server has closed the connection
                break
        except:
            break
    print("\rDisconnected from server.")
    client_socket.close()

def send_messages(client_socket):
    """Sends messages from user input."""
    try:
        while True:
            message_to_send = input(f"{NAME}: ")
            if message_to_send.lower() in ['quit', 'exit']:
                break
            client_socket.send(message_to_send.encode('utf-8'))
    except (EOFError, KeyboardInterrupt):
        # Handle Ctrl+D or Ctrl+C to gracefully exit
        print("\nDisconnecting...")
    finally:
        client_socket.close()

def start_client():
    """Prompts for a name, connects to the server, and starts threads."""
    global NAME
    # Ask the user for their name first
    NAME = input("Please enter your name to join the chat: ")
    if not NAME:
        # Provide a default name if the user enters nothing
        NAME = f"Guest-{os.getpid()}"

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client.connect((SERVER_HOST, SERVER_PORT))
        print("Connected to the chat server! Start typing to send messages.")
    except Exception as e:
        print(f"Error: Could not connect to server at {SERVER_HOST}:{SERVER_PORT}. {e}")
        return

    # Start a thread to listen for incoming messages from the server
    receive_thread = threading.Thread(target=receive_messages, args=(client,))
    receive_thread.daemon = True # Allows main program to exit even if thread is running
    receive_thread.start()
    
    # The main thread will handle sending messages
    send_messages(client)

if __name__ == "__main__":
    start_client()

