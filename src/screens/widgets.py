import tkinter as tk
from tkinter import ttk

class Widget(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)

        self.main_frame = tk.Frame(self, bg = '#272727', height = 800, width = 800)
        self.main_frame.pack(fill='both', expand = 'true')
        self.main_frame.grid_columnconfigure(0, weight = 1)
        self.main_frame.grid_rowconfigure(0, weight = 1)

class ControllPanel(Widget):

    def __init__(self, parent, controller):
        Widget.__init__(self, parent)
        frame1 = tk.LabelFrame(self, text = 'Frame 1')
        frame1.place(rely = 0.05, relx = 0.02, height = 800, width = 400)

        button1 = tk.Button(frame1, text = 'Button 1', command=lambda: print("hello"))
        button1.pack()

        treeview = ttk.Treeview(frame1)
        col_names = ['ID', 'params', 'status']

        treeview['columns'] = col_names
        treeview['show'] = 'headings'

        for col in col_names:
            treeview.heading(col, text = col)
            treeview.column(col, width = 50)
        treeview.place(relheight = 1, relwidth = 1)
        treescroll = tk.Scrollbar(frame1)
        treescroll.configure(command=treeview.yview)
        treeview.configure(yscrollcommand=treescroll.set)
        treescroll.pack(side='right', fill = 'y')
    
        for i in range(20):
            treeview.insert('', 'end', values = (i, 'default','running'))
        
        frame2 = tk.LabelFrame(self, text='Frame 2')
        frame2.place(rely = 0.05, relx = 0.5, height = 800, width=400)
        button2 = tk.Button(frame2, text = 'Button 2', command = lambda: controller._start_scraper())
        button2.pack()
    
class AnotherPanel(Widget):
    def __init__(self, parent):
        Widget.__init__(self, parent)
        label = tk.Label(self.main_frame, text = 'Label 1')
        label.pack(side = 'top')