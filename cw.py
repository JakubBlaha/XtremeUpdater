def center_window(window):
    "Moves given instance of tk.Tk ot tk.Toplevel window to the center of your screen"
    
    window.update()
    screen_width = window.winfo_screenwidth()  # obtaining information
    screen_height = window.winfo_screenheight()
    window_width = window.winfo_width()
    window_height = window.winfo_height()

    x = (screen_width // 2) - (window_width // 2)  # calculating position
    y = (screen_height // 2) - (window_height // 2)

    window.geometry(f"+{x}+{y}")  # setting position; This string formatting works only in python 3.6 and up, you may need to change this line!
