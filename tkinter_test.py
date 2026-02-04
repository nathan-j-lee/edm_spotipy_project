import tkinter as tk
from tkinter import filedialog
from tkinter.messagebox import showinfo

def prompt_user():
    #Create hidden root window so only the dialog appears

    print("Running prompt user function...")

    root = tk.Tk()
    root.withdraw()

    filetypes = (
    ('text files', '*.txt'),
    ('All files', '*.*')
    )

    filename = filedialog.askopenfilename(
        title='Open file',
        initialdir='/',
        filetypes=filetypes
    )
    print(f'Path of file: {filename}')
    return filename