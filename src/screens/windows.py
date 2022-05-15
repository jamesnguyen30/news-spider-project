import tkinter as tk

class NewWindow(tk.Tk):

    def  __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        main_frame = tk.Frame(self, bg = '#272727', height = 300, width = 300)

        main_frame.pack_propagate(0)
        main_frame.pack(fill = 'both', expand = 'true')

        self.geometry('300x300')
        self.resizable(0,0)
        self.title('New Window')

        label1 = tk.Label(main_frame, text = 'New Label')
        label1.grid(row = 1, column = 0)

        label2 = tk.Label(main_frame, text = "Label 2")
        label2.grid(row = 2, column = 0)