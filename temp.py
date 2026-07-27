import tkinter as tk
from tkinter import ttk
import time
from datetime  import datetime

# Python program to demonstrate
# scale widget

from tkinter import * 


root = Tk()  
root.geometry("400x300") 

v1 = DoubleVar()

def show1():      
    sel = "Horizontal Scale Value = " + str(v1.get())
    l1.config(text = sel, font =("Courier", 14))  
    print("Current value = ", v1.get(), type(v1.get()), int(v1.get()))

s1 = Scale( root, variable = v1, from_ = 1, to = 100, orient = HORIZONTAL, length=200, width = 20)   
l3 = Label(root, text = "Horizontal Scaler")
b1 = Button(root, text ="Display Horizontal", command = show1, bg = "yellow")  
l1 = Label(root)

s1.set(50)

s1.pack(anchor = CENTER) 
l3.pack()
b1.pack(anchor = CENTER)
l1.pack() 

root.mainloop()



# t_start = datetime.now().second
# time.sleep(1)
# t_stop = datetime.now().second
# print(t_stop - t_start)

# def start_task():
#     # Loop to simulate a loading process
#     for i in range(1, 101):
#         time.sleep(0.05)  # Simulate work
        
#         # Update progress bar value
#         progress_bar['value'] = i
        
#         # Refresh the GUI immediately to show the change
#         root.update_idletasks() 

# root = tk.Tk()
# root.title("Determinate Progress Bar")
# root.geometry("300x150")

# # Create the progress bar
# progress_bar = ttk.Progressbar(root, orient="horizontal", length=200, mode="determinate")
# progress_bar.pack(pady=20)

# # Button to trigger the work
# start_btn = ttk.Button(root, text="Start", command=start_task)
# start_btn.pack(pady=10)

# root.mainloop()
