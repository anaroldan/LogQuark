import tkinter as tk
import time
from time import gmtime, strftime
import os
class TextLineNumbers(tk.Canvas):
    def __init__(self, *args, **kwargs):
        tk.Canvas.__init__(self, *args, **kwargs)
        self.textwidget = None
        self.lastline =  1
        self.lineatbeginning = 0
        self.firstwrite = True
        self.filename = ""

    def attach(self, text_widget, file_name):
        self.textwidget = text_widget
        self.filename = file_name
        try:
            log = open(self.filename, "r")
            for c,l in enumerate(log):
                if len(l.split("|")) >= 2:
                    self.textwidget.insert("%d.0" % (c+1), l.split("|")[1])
                else:
                    print ("error")
            self.lineatbeginning = c + 1
        except FileNotFoundError:
            pass

    def redraw(self, *args):
        '''redraw line numbers'''
        self.delete("all")

        i = self.textwidget.index("@0,0")
        hours = []
        empty_lines = 0
        count = 0
        try:
            log = open(self.filename, "r")
            for c,l in enumerate(log):
                count  = c + 1
                if len(l.split("|")) >= 2:
                    hours.append(l.split("|")[0])
                else:
                    empty_lines = empty_lines + 1
                    pass
            log.close()
        except FileNotFoundError:
            pass

        self.lastline = count - empty_lines  + 1

        while True :
            dline= self.textwidget.dlineinfo(i)
            if dline is None: break
            y = dline[1]
            linenum = str(i).split(".")[0]
            line_text = self.textwidget.get("%d.0" % int(linenum), "%d.end" % int(linenum))

            if (int(linenum)) > self.lastline:
                if self.lineatbeginning < (int(linenum) + 2):
                    last_line = self.textwidget.get("%d.0" % (int(linenum)-1), "%d.end" % (int(linenum)-1))
                    log = open(self.filename, "a")
                    if self.lineatbeginning == 0 and self.firstwrite is True:
                        self.firstwrite = False
                        log.write(heure +  "|" + last_line)
                    else:
                        log.write("\n" + heure + "|" + last_line)
                self.lastline = int(linenum)

            if (len(line_text) >= 1) and self.lastline == int(linenum):
                heure = strftime("%H:%M:%S", time.localtime())
                if len(hours) < self.lastline:
                     hours.append(heure)

            if (int(linenum) <= self.lastline and len(line_text) >= 1):
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
        folder = os.path.dirname(os.path.realpath(__file__))    # getting folder path for any os
        month = strftime("%m", time.localtime())
        year = "20" + strftime("%y", time.localtime())
        file_name = strftime("%d", time.localtime())
        self.winfo_toplevel().title(year + "/" + month + "/" + file_name)
        file_path = os.path.join(folder, year, month, file_name)

        try:
            os.mkdir(os.path.join(folder, year))
        except:
            pass

        try:
            os.mkdir(os.path.join(folder, year, month))
        except:
            pass

        self.linenumbers.attach(self.text, file_path + ".txt")

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
