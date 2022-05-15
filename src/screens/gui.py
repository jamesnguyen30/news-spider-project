import tkinter as tk
from widgets import ControllPanel, AnotherPanel
from windows import NewWindow

# class Widget(tk.Frame):
#     def __init__(self, parent):
#         tk.Frame.__init__(self, parent)

#         self.main_frame = tk.Frame(self, bg = '#272727', height = 800, width = 800)
#         self.main_frame.pack(fill='both', expand = 'true')
#         self.main_frame.grid_columnconfigure(0, weight = 1)
#         self.main_frame.grid_rowconfigure(0, weight = 1)

# class ControllPanel(Widget):

#     def __init__(self, parent):
#         Widget.__init__(self, parent)
#         frame1 = tk.LabelFrame(self, text = 'Frame 1')
#         frame1.place(rely = 0.05, relx = 0.02, height = 300, width = 300)

#         button1 = tk.Button(frame1, text = 'Button 1', command=lambda: print("hello"))
#         button1.pack()

# class NewWindow(tk.Tk):

#     def  __init__(self, *args, **kwargs):
#         tk.Tk.__init__(self, *args, **kwargs)

#         main_frame = tk.Frame(self, bg = '#272727', height = 300, width = 300)

#         main_frame.pack_propagate(0)
#         main_frame.pack(fill = 'both', expand = 'true')

#         self.geometry('300x300')
#         self.resizable(0,0)
#         self.title('New Window')

#         label1 = tk.Label(main_frame, text = 'New Label')
#         label1.grid(row = 1, column = 0)

#         label2 = tk.Label(main_frame, text = "Label 2")
#         label2.grid(row = 2, column = 0)

class MenuBar(tk.Menu):

    def __init__(self, parent):

        tk.Menu.__init__(self, parent)

        menu1 = tk.Menu(self, tearoff=0)
        menu1.add_command(label = 'Control Panel', command = lambda: parent.show_controll_panel())
        menu1.add_command(label = 'Another Panel', command = lambda: parent.show_another_panel())
        menu1.add_command(label = 'Option 3', command = lambda: print("Menu 1 Option 3 clicked"))
        menu1.add_separator()
        menu1.add_command(label = 'Option 4', command = lambda: print("Menu 1 Option 4 clicked"))

        self.add_cascade(label = "Menu 1", menu = menu1)

        menu2 = tk.Menu(self, tearoff=0)
        menu2.add_command(label = 'Option 1', command = lambda: print("Menu 2 Option 1 clicked"))
        menu2.add_command(label = 'Option 2', command = lambda: print("Menu 2 Option 2 clicked"))
        menu2.add_command(label = 'Option 3', command = lambda: print("Menu 2 Option 3 clicked"))
        menu2.add_separator()
        menu2.add_command(label = 'Option 4', command = lambda: print("Menu 2 Option 4 clicked"))

        self.add_cascade(label = "Menu 2", menu = menu2)

class MyApp(tk.Tk):

    def __init__(self, *args, **kwargs):

        tk.Tk.__init__(self, *args, **kwargs)
        self.main_frame = tk.Frame(self, bg = '#272727', height = 800, width = 600)
        # main_frame.geometry('800x600')
        self.main_frame.pack_propagate(0)
        self.main_frame.pack(fill='both', expand = 'true')
        self.main_frame.grid_columnconfigure(0, weight = 1)
        self.main_frame.grid_rowconfigure(0, weight = 1)

        menubar = MenuBar(self)
        tk.Tk.config(self, menu = menubar)

        self.show_controll_panel()

    def show_controll_panel(self):
        print('shoing control panel')
        frame = ControllPanel(self.main_frame)
        # frame.grid(row = 0, column = 0, sticky='nsew')
        # frame.tkraise()
        self._show_widget(frame)
    
    def show_another_panel(self):
        print("showing another panel")
        w = AnotherPanel(self.main_frame)
        self._show_widget(w)
    
    def _show_widget(self, widget):
        widget.grid(row = 0, column = 0, sticky = 'nsew')
        widget.tkraise()

if __name__ == '__main__':
    root = MyApp()
    root.title('My app')
    root.mainloop()
