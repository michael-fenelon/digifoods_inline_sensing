import tkinter as tk

def draw_grid():
    # Clear any previous lines before redrawing
    canvas.delete("grid_line")
    
    # Get current canvas dimensions
    width = canvas.winfo_width()
    height = canvas.winfo_height()
    
    # Set the distance between grid lines (cell size)
    grid_size = 40
    
    # Draw vertical lines
    for x in range(0, width, grid_size):
        canvas.create_line(x, 0, x, height, fill="#CCCCCC", tags="grid_line")
        
    # Draw horizontal lines
    for y in range(0, height, grid_size):
        canvas.create_line(0, y, width, y, fill="#CCCCCC", tags="grid_line")

# Set up the main application window
root = tk.Tk()
root.title("2D Canvas Grid")
root.geometry("600x400")

# Create the canvas widget
canvas = tk.Canvas(root, bg="white")
canvas.pack(fill=tk.BOTH, expand=True)

draw_grid()

# Bind the resize event to trigger the grid drawing
# canvas.bind("<Configure>", draw_grid)

root.mainloop()
