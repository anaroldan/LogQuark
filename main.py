import tkinter as tk
import time
from time import gmtime, strftime
class TextLineNumbers(tk.Canvas):
    def __init__(self, *args, **kwargs):
        tk.Canvas.__init__(self, *args, **kwargs)
        self.textwidget = None
        self.lastline =  1

    def attach(self, text_widget):
        self.textwidget = text_widget
        log = open("test.txt", "r")

        texts = []

        for c,l in enumerate(log):
            if len(l.split("|")) >= 2:
                self.textwidget.insert("%d.0" % (c+1), l.split("|")[1])
            else:
                print ("error")

    def redraw(self, *args):
        '''redraw line numbers'''
        self.delete("all")

        i = self.textwidget.index("@0,0")
        log = open("test.txt", "r")

        texts = []
        hours = []

        for c,l in enumerate(log):
            if len(l.split("|")) >= 2:
                hours.append(l.split("|")[0])
            else:
                pass

        lastlinenumber = c + 1
        self.lastline = c + 1

        while True :
            dline= self.textwidget.dlineinfo(i)
            if dline is None: break
            y = dline[1]
            linenum = str(i).split(".")[0]

            if (int(linenum) - 1) >= self.lastline:
                log = open("test.txt", "a")
                heure = strftime("%H:%M:%S", time.localtime())
                log.write("\n" + heure +  " | nouvelle heure")
                hours.append(heure)
                log.close()
                self.lastline = int(linenum)
            print(linenum + " and last: " + str(self.lastline))
            if (int(linenum) < self.lastline):
                self.create_text(2,y,anchor="nw", text=(linenum+" "+hours[int(linenum)-1]))
            else:
                self.create_text(2,y,anchor="nw", text=linenum)

            i = self.textwidget.index("%s+1line" % i)

class CustomText(tk.Text):
    def __init__(self, *args, **kwargs):
        tk.Text.__init__(self, *args, **kwargs)

        self.tk.eval('''
            proc widget_proxy {widget widget_command args} {

                # call the real tk widget command with the real args
                set result [uplevel [linsert $args 0 $widget_command]]

                # generate the event for certain types of commands
                if {([lindex $args 0] in {insert replace delete}) ||
                    ([lrange $args 0 2] == {mark set insert}) ||
                    ([lrange $args 0 1] == {xview moveto}) ||
                    ([lrange $args 0 1] == {xview scroll}) ||
                    ([lrange $args 0 1] == {yview moveto}) ||
                    ([lrange $args 0 1] == {yview scroll})} {

                    event generate  $widget <<Change>> -when tail
                }

                # return the result from the real widget command
                return $result
            }
            ''')
        self.tk.eval('''
            rename {widget} _{widget}
            interp alias {{}} ::{widget} {{}} widget_proxy {widget} _{widget}
        '''.format(widget=str(self)))


class Window(tk.Frame):
    def __init__(self, *args, **kwargs):
        tk.Frame.__init__(self, *args, **kwargs)
        self.text = CustomText(self)
        self.vsb = tk.Scrollbar(orient="vertical", command=self.text.yview)
        self.text.configure(yscrollcommand=self.vsb.set)
        self.text.tag_configure("bigfont", font=("Helvetica", "12", "bold"))
        self.linenumbers = TextLineNumbers(self, width=80)
        self.linenumbers.attach(self.text)

        self.vsb.pack(side="right", fill="y")
        self.linenumbers.pack(side="left", fill="y")
        self.text.pack(side="right", fill="both", expand=True)

        self.text.bind("<<Change>>", self._on_change)
        self.text.bind("<Configure>", self._on_change)

    def _on_change(self, event):
        self.linenumbers.redraw()

if __name__ == "__main__":
    root = tk.Tk()
    Window(root).pack(side="top", fill="both", expand=True)
    root.mainloop()
