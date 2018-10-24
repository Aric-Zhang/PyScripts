from tkinter import *


def frame(master):
    w = Frame(master)
    w.pack(side=TOP, expand=YES, fill=BOTH)
    return w


def button(master, text, command):
    w = Button(master, text=text, command=command, width=6)
    w.pack(side=LEFT, expand=YES, fill=BOTH, padx=2, pady=2)
    return w


def back(text):
    if len(text) > 0:
        return text[:-1]
    else:
        return text


def calculate(text):
    try:
        return eval(text)
    except (SyntaxError, ZeroDivisionError, NameError):
        return 'Error'


root = Tk()
root.title("Calculator v 0.1")
text = StringVar()

Entry(root, textvariable=text).pack(expand=YES, fill=BOTH, padx=2, pady=4)

firstRow = frame(root)
button(firstRow, 'BS', lambda t=text: t.set(back(t.get())))
button(firstRow, 'C', lambda t=text: t.set(''))
button(firstRow, '(', lambda t=text: t.set(t.get() + '('))
button(firstRow, ')', lambda t=text: t.set(t.get() + ')'))

for keyStr in ('789/', '456*', '123-', '0.=+'):
    buttonPanel = frame(root)
    for opName in keyStr:
        if opName == '=':
            button(buttonPanel, opName, lambda t=text: t.set(calculate(t.get())))
        else:
            button(buttonPanel, opName, lambda t=text,
                   c=opName: t.set(t.get() + c))

root.mainloop()
