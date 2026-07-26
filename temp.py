import tkinter as tk
from tkinter import ttk
import time

def start_task():
    # Loop to simulate a loading process
    for i in range(1, 101):
        time.sleep(0.05)  # Simulate work
        
        # Update progress bar value
        progress_bar['value'] = i
        
        # Refresh the GUI immediately to show the change
        root.update_idletasks() 

root = tk.Tk()
root.title("Determinate Progress Bar")
root.geometry("300x150")

# Create the progress bar
progress_bar = ttk.Progressbar(root, orient="horizontal", length=200, mode="determinate")
progress_bar.pack(pady=20)

# Button to trigger the work
start_btn = ttk.Button(root, text="Start", command=start_task)
start_btn.pack(pady=10)

root.mainloop()
