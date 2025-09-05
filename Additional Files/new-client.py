# chat_client_broadcast.py
# Connects to the broadcast server to send and receive messages simultaneously.

import socket
import threading

# --- Configuration ---
SERVER_IP = '192.168.110.150' # <-- CHANGE THIS to the server's IP
PORT = 65432
NAME = "gajendra"         # <-- CHANGE THIS to your desired name

# --- Functions ---
def receive_messages(client_socket):
    """
    Listens for incoming messages from the server and prints them.
    This runs in a separate thread.
    """
    while True:
        try:
            message = client_socket.recv(1024).decode('utf-8')
            if not message:
                print("Disconnected from server.")
                break
            # Use a carriage return to ensure the new message doesn't mess up the input line
            print('\r' + message + '\n' + f"{NAME}: ", end='')
        except ConnectionResetError:
            print("\nConnection to the server was lost.")
            break
        except Exception as e:
            print(f"An error occurred: {e}")
            break

def start_client():
    """
    Connects to the server and starts threads for sending/receiving.
    """
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client.connect((SERVER_IP, PORT))
        print("Connected to the chat server! Start typing to send messages.")
    except ConnectionRefusedError:
        print("Connection failed. Is the server running?")
        return
    
    # Start the thread that will listen for incoming messages
    receive_thread = threading.Thread(target=receive_messages, args=(client,))
    receive_thread.daemon = True # Allows main program to exit
    receive_thread.start()

    # Main thread will handle user input for sending messages
    try:
        while True:
            # Use the NAME variable as the prompt for the user's input
            message = input(f"{NAME}: ")
            if message:
                # The raw message is sent; the server adds the sender's IP
                client.send(message.encode('utf-8'))
    except (KeyboardInterrupt, EOFError):
        print("\nClosing connection.")
    finally:
        client.close()

if __name__ == "__main__":
    start_client()


# # chat_client_broadcast.py
# # Connects to the broadcast server to send and receive messages simultaneously.

# import socket
# import threading

# # --- Configuration ---
# SERVER_IP = '192.168.110.150' # <-- CHANGE THIS to the server's IP
# PORT = 65432

# # --- Functions ---
# def receive_messages(client_socket):
#     """
#     Listens for incoming messages from the server and prints them.
#     This runs in a separate thread.
#     """
#     while True:
#         try:
#             message = client_socket.recv(1024).decode('utf-8')
#             if not message:
#                 print("Disconnected from server.")
#                 break
#             print(message)
#         except ConnectionResetError:
#             print("Connection to the server was lost.")
#             break
#         except Exception as e:
#             print(f"An error occurred: {e}")
#             break

# def start_client():
#     """
#     Connects to the server and starts threads for sending/receiving.
#     """
#     client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#     try:
#         client.connect((SERVER_IP, PORT))
#         print("Connected to the chat server! Start typing to send messages.")
#     except ConnectionRefusedError:
#         print("Connection failed. Is the server running?")
#         return
    
#     # Start the thread that will listen for incoming messages
#     receive_thread = threading.Thread(target=receive_messages, args=(client,))
#     receive_thread.daemon = True # Allows main program to exit
#     receive_thread.start()

#     # Main thread will handle user input for sending messages
#     try:
#         while True:
#             message = input()
#             if message:
#                 client.send(message.encode('utf-8'))
#     except KeyboardInterrupt:
#         print("\nClosing connection.")
#     finally:
#         client.close()

# if __name__ == "__main__":
#     start_client()
