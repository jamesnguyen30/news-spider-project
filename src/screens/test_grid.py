import tkinter as tk

if __name__ == '__main__':
    root = tk.Tk()
    root.title("test")
    root.geometry('800x600')

    container = tk.Frame(root,width = 800, height = 600)
    container.grid(row = 0, column = 0, sticky='n')

    # container1 = tk.Frame(root,width = 800, height = 600)
    # container1.grid(row = 2, column = 0, sticky='n')

    frame1 = tk.LabelFrame(container, text = 'Frame 1',bg = 'cyan', width = 400, height = 400)
    frame2 = tk.LabelFrame(container, text = 'Frame 2',bg = 'blue', width = 400, height = 50)
    frame3 = tk.LabelFrame(container, text = 'Frame 3',bg = 'yellow', width = 400, height = 50)
    frame4 = tk.LabelFrame(container, text = 'Frame 4',bg = 'green', width = 400, height = 50)
    frame5 = tk.LabelFrame(container, text = 'Frame 5',bg = 'red', width = 400, height = 50)
    frame6 = tk.LabelFrame(container, text = 'Frame 6',bg = 'black', width = 400, height = 50)

    # frame7 = tk.Frame(container1, bg = 'black', width = 400, height = 50)
    # frame8 = tk.Frame(container, bg = 'red', width = 400, height = 50)
    # frame9 = tk.Frame(container, bg = 'green', width = 400, height = 50)
    # frame10 = tk.Frame(container, bg = 'yellow', width = 400, height = 50)

    root.grid_columnconfigure(0, weight = 1)
    # root.grid_rowconfigure(0, weight = 1)
    # root.grid_rowconfigure(1, weight = 1)
    # root.grid_rowconfigure(2, weight = 1)

    frame1.grid(row = 0, sticky = 'w')
    frame2.grid(row = 1, sticky = 'w')
    frame3.grid(row = 2, sticky = 'w')

    frame4.grid(row = 0, column=1, sticky='w')
    frame5.grid(row = 1, column=1, sticky='w')
    frame6.grid(row = 2, column=1, sticky='w')

    # frame7.grid(row = 0, column=0, sticky='w')
    # frame8.grid(row = 1, column=0, sticky='w')
    # frame9.grid(row = 0, column=1, sticky='w')
    # frame10.grid(row = 1, column=1, sticky='w')

    root.mainloop()


