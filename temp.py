import tkinter as tk
from tkinter import ttk

root = tk.Tk()
root.geometry("400x400")

# 1. Create Notebook and Tab Frame
notebook = ttk.Notebook(root)
notebook.pack(fill="both", expand=True)

tab1 = ttk.Frame(notebook)
tab2 = ttk.Frame(notebook)
notebook.add(tab1, text=" Tab 1")
notebook.add(tab2, text=" Tab 2")

# 2. Create Parent Canvas inside the Tab
parent_canvas = tk.Canvas(tab1, bg="lightgray", width=350, height=350)
parent_canvas.pack(padx=20, pady=20)

# 3. Create Child Canvas with parent_canvas as its master
child_canvas = tk.Canvas(parent_canvas, bg="lightblue", width=150, height=150)

# 4. Place child canvas onto parent canvas using create_window
parent_canvas.create_window(50, 50, window=child_canvas, anchor="nw")

root.mainloop()
