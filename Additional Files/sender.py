# sender.py
# This script runs on the machine that will send the message.

import socket

# --- Configuration ---
# IMPORTANT: Change this to the IP address of the receiver machine.
RECEIVER_IP = '192.168.110.135' # <-- CHANGE THIS
# The port must match the port used by the receiver script.
PORT = 65432

print("--- Sender Script ---")
print(f"Attempting to connect to {RECEIVER_IP}:{PORT}")

# Get the message to send from the user
message_to_send = input("Enter the message you want to send: ")

# Use a 'with' statement to automatically close the socket
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    try:
        # Connect to the server
        s.connect((RECEIVER_IP, PORT))
        print("Successfully connected to the receiver.")
        
        # Encode the string message into bytes (using UTF-8) and send it
        s.sendall(message_to_send.encode('utf-8'))
        print("Message sent.")
        
        # Wait to receive a confirmation from the server
        confirmation = s.recv(1024)
        print(f"Server response: {confirmation.decode('utf-8')}")

    except ConnectionRefusedError:
        print("Connection failed. Is the receiver script running?")
    except socket.gaierror:
        print(f"Hostname could not be resolved. Is the IP address '{RECEIVER_IP}' correct?")
    except Exception as e:
        print(f"An error occurred: {e}")
