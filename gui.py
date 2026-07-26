import socket
import tkinter as tk

class ControlledApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Controlled App")
        self.root.geometry("300x150")

        # UI Elements
        self.label = tk.Label(root, text="Waiting for external command...", font=("Arial", 12))
        self.label.pack(pady=20)
        
        self.status_indicator = tk.Label(root, text="Status: Idle", fg="blue")
        self.status_indicator.pack()

        # Set up the non-blocking IPC Socket Server
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind(('127.0.0.1', 65432)) # Localhost port
        self.server_socket.listen(1)
        self.server_socket.setblocking(False) # Prevents the socket from freezing the GUI

        # Start checking for external messages safely
        self.listen_for_commands()

    def listen_for_commands(self):
        try:
            # Check if an external script is trying to connect
            client_socket, _ = self.server_socket.accept()
            message = client_socket.recv(1024).decode('utf-8').strip()
            client_socket.close()

            if message:
                self.process_command(message)
        except BlockingIOError:
            # No incoming connections yet; this is expected behavior
            pass

        # Schedule the next check in 100ms without blocking the main loop
        self.root.after(100, self.listen_for_commands)

    def process_command(self, command):
        """Routes external commands to specific GUI updates."""
        if command.startswith("UPDATE_TEXT:"):
            new_text = command.split(":", 1)[1]
            self.label.config(text=new_text)
        elif command == "SET_ACTIVE":
            self.status_indicator.config(text="Status: Active", fg="green")
        elif command == "SET_IDLE":
            self.status_indicator.config(text="Status: Idle", fg="blue")
        elif command == "CLOSE":
            self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = ControlledApp(root)
    root.mainloop()
