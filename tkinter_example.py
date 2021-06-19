import tkinter as tk

class App(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.pack()

        self.entrythingy = tk.Entry()
        self.entrythingy.pack()

        # Create the application variable.
        self.contents = tk.StringVar()
        # Set it to some value.
        self.contents.set("this is a variable")
        # Tell the entry widget to watch this variable.
        self.entrythingy["textvariable"] = self.contents

        # Define a callback for when the user hits return.
        # It prints the current value of the variable.
        self.entrythingy.bind('<Key-Return>',
                             self.print_contents)

    def print_contents(self, event):
        print("Hi. The current entry content is:",
              self.contents.get())

root = tk.Tk()
myapp = App(root)
myapp.mainloop()
# %%
import tkinter as tk

class App(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.pack()
        self.create_widgets()
        self.button.bind("<Enter>", self.turn_red)

    def turn_red(self, event):
        event.widget["activeforeground"] = "red"
        print("red")

    def create_widgets(self):

        self.inputStonk = tk.Entry(self)
        self.inputStonk.insert(0,"BNBTRY")
        self.inputStonk.pack()

        self.button = tk.Button(self)
        self.button["text"] = "Hello World\n(click me)"
        # self.hi_there["command"] = self.start_scan
        self.button.pack(side="top")

        self.a1 = tk.Message(self)
        self.a1["text"] = "place me here"
        self.a1.pack(side="bottom")


        self.quit = tk.Button(self, text="QUIT", fg="red",
                              command=self.master.destroy)
        self.quit.pack(side="bottom")

    

# create the application
myapp = App()

#
# here are method calls to the window manager class
#
myapp.master.title("My Do-Nothing Application")
myapp.master.maxsize(1000, 400)

# start the program
myapp.mainloop()