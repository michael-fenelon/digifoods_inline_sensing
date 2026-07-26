import socket
import time

def send_command(command_string):
    """Establishes a brief connection to pass an instruction to the Tkinter app."""
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(('127.0.0.1', 65432))
        client.sendall(command_string.encode('utf-8'))
        client.close()
        print(f"Sent: {command_string}")
    except ConnectionRefusedError:
        print("Error: Could not connect to the Tkinter application. Is it running?")

# Simulating remote automation control
if __name__ == "__main__":
    print("Starting external automation sequence...")
    time.sleep(1)
    
    # 1. Change text remotely
    send_command("UPDATE_TEXT:Hello from the External Script!")
    time.sleep(2)
    
    # 2. Change state remotely
    send_command("SET_ACTIVE")
    time.sleep(2)
    
    # 3. Revert state remotely
    send_command("SET_IDLE")


