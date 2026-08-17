import tkinter as tk

def change_text():
    label.config(text="Status: Processing...")
    # Pause for 2000 milliseconds (2 seconds), then call 'complete_task'
    root.after(2000, complete_task)

def complete_task():
    label.config(text="Status: Done!")

root = tk.Tk()
label = tk.Label(root, text="Status: Ready")
label.pack(pady=10)

btn = tk.Button(root, text="Start", command=change_text)
btn.pack()

root.mainloop()
