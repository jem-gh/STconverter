#!/usr/bin/python


###############################################################################
# SimpleGUI/Tkinter Converter (STconverter.py) is a little software aiming to 
# convert simple Python scripts written for SimpleGUI to work with Tkinter GUI 
# module instead, and vice versa.
# 
# "Tkinter is Python's de-facto standard GUI (Graphical User Interface) package"
# (http://wiki.python.org/moin/TkInter)
# "SimpleGUI is a custom Python graphical user interface (GUI) module implemented 
# directly in CodeSkulptor that provides an easy to learn interface for building 
# interactive programs in Python" (http://www.codeskulptor.org) used for the 
# online Coursera course "An Introduction to Interactive Programming in Python" 
# by Joe Warren, Scott Rixner, John Greiner, and Stephen Wong (Rice University) 
# 
# For latest version of SimpleGUI/Tkinter Converter or detailed changelog, visit 
# the repository on Github: 
# https://github.com/jem-gh/STconverter
# 
# SimpleGUI/Tkinter Converter is developed by Jean-Etienne Morlighem
###############################################################################


# global modules
import re


# global variables
input_data = ""
input_name = ""
output_data = ""



class Simplegui2Tkinter:
    def __init__(self, input_data):
        """ update SimpleGUI parts to Tkinter """
        
        global output_data
        
        # stop conversion if the input file do not use the simplegui module
        if not "simplegui" in input_data:
            output_data = "___NoSimpleguiFound!___"
            return
        
        self.up_module()
        self.up_frame_canvas()
        self.up_button()
        self.up_label()
        self.up_input()
        self.up_ini()
    
    
    def up_module(self):
        """ update simplegui module to Tkinter """
        global output_data
        MODULE_RE = re.compile(r'^(import [\w ,]*)simplegui', re.MULTILINE)
        output_data = MODULE_RE.sub(r'\1Tkinter', input_data)
    
    
    def up_frame_canvas(self):
        """ update the Frame and Canvas widget """
        
        global output_data
        
        frame_widget = {
        "sg_frame":  "^(\w+) ?= ?simplegui.create_frame" + \
                     "\((\".+\"), ?(\d+), ?(\d+)(?:, ?\d+)?\)", 
        "tk_frame":  "window_root = Tkinter.Tk()\n" + \
                     "window_root.title(\\2)\n" + \
                     "\\1 = Tkinter.Frame(window_root)\n" + \
                     "\\1.grid()\n"}
        canvas_widget = {
        "tk_canvas": "w_canvas = Tkinter.Canvas(\\1, width=\\3, height=\\4)\n" + \
                     "w_canvas.grid()\n", 
        "sg_txt": "\w+.draw_text\((.+), ?" + \
                  "[\[\(](\d+), (\d+)[\]\)], (\d+), (\"\w+\")\)", 
        "tk_txt": "w_canvas.create_text((\\2, \\3), anchor='sw', " + \
                  "text=\\1, font=('DejaVu Serif Condensed', \\4), fill=\\5)"}
        
        FRAME_RE = re.compile(r'%s' % frame_widget["sg_frame"], re.MULTILINE)
        
        # if no need for Canvas widget, update only the Frame
        if "set_draw_handler" not in output_data:
            output_data = FRAME_RE.sub(r'%s' % frame_widget["tk_frame"], output_data)
            return
        
        
        # find name of drawing handler
        draw_handler = re.findall(r'^\w+.set_draw_handler\((.+)\)', output_data, 
                                  re.MULTILINE)[0]
        
        # find all global variables used in code
        global_var_str = ''.join(re.findall(r'^\s+global([ \w+,]+)', output_data, 
                                            re.MULTILINE))
        global_var_list = re.findall(r'(\w+)+', global_var_str)
        
        # select only global variables used in drawing handler
        global_var_drw = []
        for var in global_var_list:
            global_var_drw += re.findall(
                  r'^def %s\(\w+\):(?:\n .*)+[=( \-+*/](%s)[) \-+*/]*' % 
                   (draw_handler, var), output_data, re.MULTILINE)
        
        # update functions containing global variables used by drawing handler
        for var in global_var_drw:
            fn_old = re.findall(r'(^\s+global .*%s(?:.*\n)+?)\n\S' % var, 
                                output_data, re.MULTILINE)[0]
            space = re.findall(r'(    +?)global', fn_old)[0]
            fn_new = fn_old[:-1] + space + draw_handler + "()\n\n"
            output_data = re.sub(re.escape(fn_old), fn_new, output_data)
        
        # update drawing handler
        DH_RE = re.compile(r'^def (%s)\(\w+\):\n(\s+)' % draw_handler, re.MULTILINE)
        output_data = DH_RE.sub(r'def \1():\n\2w_canvas.delete("all")\n\2', output_data)
        
        # create canvas with size used in "simplegui.create_frame"
        output_data = FRAME_RE.sub(r'%s\n%s' % (frame_widget["tk_frame"], 
                                   canvas_widget["tk_canvas"]), output_data)
        
        # delete "set_draw_handler" and replace with drawing handler call
        output_data = re.sub(r'\w+.set_draw_handler\(%s\)' % draw_handler, 
                             draw_handler+"()\n", output_data)
        
        # update Canvas methods
        # Text
        TXT_RE = re.compile(r'%s' % canvas_widget["sg_txt"], re.MULTILINE)
        output_data = TXT_RE.sub(r'%s' % canvas_widget["tk_txt"], output_data)
        
        # Oval
        if ".draw_circle" in output_data:
            x, y, r, w = re.findall(r".draw_circle\([\[\(](\d+), (\d+)[\]\)], " + \
                                     "(\d+), (\d+)", output_data)[0]
            x, y = (int(x) - int(r) / 2), (int(y) + int(r) / 2)
            output_data = re.sub(r'\w+.draw_circle.*(\"\w+\").+\n', 
                                 r'w_canvas.create_oval((%d,%d,%d,%d), width=%s, outline=\1, fill="")\n' % 
                                 (x, x, y, y, w), output_data)
    
    
    def up_button(self):
        """ update Button widget(s) """
        global output_data
        button_widget = {
        "sg_button": "^(\w+).add_button\((.+), ?(\w+), ?\d+\)", 
        "tk_button": "\\3_bt = Tkinter.Button(\\1, text=\\2, command=\\3)\n" + \
                     "\\3_bt.grid()\n"}
        BUTTON_RE = re.compile(r"%s" % button_widget["sg_button"], re.MULTILINE)
        output_data = BUTTON_RE.sub(r"%s" % button_widget["tk_button"], output_data)
    
    
    def up_label(self):
        """ update Label widget(s) """
        pass
        #### Tkinter.Label(window_root, text="")
    
    
    def up_input(self):
        """ update Entry/Input widget(s) """
        
        global output_data
        
        if "add_input" in output_data:
            
            input_widget = {
            "input_name":    "^\w+.add_input\(.+, ?(\w+), ?\d+\)", 
            "param_name":    "^def %s\((\w+)\):", 
            "handler":       "^def %s\(%s\):(?:\n .*)+[=( \-+*/]%s[) \-+*/]", 
            "handler_param": "(?<=(?<!%s)[= \(\-+*/])%s(?=[ \)\-+*/\n])", 
            "sg_input":      "^(\w+).add_input\((.+), ?(\w+), ?(\d+)\)", 
            "tk_input":      "\\3_lb = Tkinter.Label(\\1, text=\\2)\n" + \
                             "\\3_lb.grid()\n" + \
                             "\\3_et = Tkinter.Entry(\\1)\n" + \
                             "\\3_et.bind('<Return>', \\3)\n" + \
                             "\\3_et.grid()\n"}
            
            # retrieve all Input widgets and respective handler names
            input_names = re.findall(r'%s' % input_widget["input_name"], 
                                     output_data, re.MULTILINE)
            
            for input_name in input_names:
                # retrieve parameter name used in the Input handler
                param_name = re.findall(input_widget["param_name"] % input_name, 
                                        output_data, re.MULTILINE)[0]
                
                # find and update parameter in the Input handler
                HANDLER_RE = re.compile(input_widget["handler"] % (input_name, 
                                        param_name, param_name), re.MULTILINE)
                
                handler_old = re.findall(HANDLER_RE, output_data)[0]
                handler_new = re.sub(input_widget["handler_param"] % 
                                     (input_name, param_name), 
                                     "%s_et.get()" % input_name, handler_old)
                
                output_data = output_data.replace(handler_old, handler_new)
                
                ## write Tkinter GUI of the Input widget
                INPUT_RE = re.compile(r'%s' % input_widget["sg_input"], re.MULTILINE)
                output_data = INPUT_RE.sub(r"%s" % input_widget["tk_input"], 
                                           output_data)
    
    
    def up_ini(self):
        """ update the initialization of the event loop """
        global output_data
        START_RE = re.compile(r'^\w+.start\(\)', re.MULTILINE)
        output_data = START_RE.sub("window_root.mainloop()\n", output_data)




########## GUI of the application ##########

# import modules
import Tkinter, tkFileDialog, tkMessageBox


class Window_App:
    def __init__(self, master):
        """ core of the GUI """
        
        # Frame
        frame = Tkinter.Frame(master)
        frame.grid()
        frame.rowconfigure(0, minsize=40)
        frame.rowconfigure(3, minsize=40)
        frame.rowconfigure(5, minsize=60)
        frame.rowconfigure(7, minsize=60)
        
        title_text = "SimpleGUI/Tkinter converter"
        label_title = Tkinter.Label(frame, text=title_text)
        label_title.grid(row=0, columnspan=2)
        
        
        # input: select file to convert
        label_open = Tkinter.Label(frame, text="File to convert:")
        label_open.grid(row=1, column=0, sticky="W", padx=10)
        
        self.entry_open = Tkinter.Entry(frame, width=40)
        self.entry_open.grid(row=2, column=0, sticky="W", padx=10)
        
        self.button_open = Tkinter.Button(frame, text="Select file", 
                                          command=self.file_open, width=11)
        self.button_open.grid(row=2, column=1, sticky="W", padx=10)
        
        
        # output: select name and directory for saving conversion
        label_save = Tkinter.Label(frame, text="Save as:")
        label_save.grid(row=3, column=0, sticky="W"+"S", padx=10)
        
        self.entry_save = Tkinter.Entry(frame, width=40)
        self.entry_save.grid(row=4, column=0, sticky="W", padx=10)
        
        self.button_save = Tkinter.Button(frame, text="Select directory", 
                                          command=self.directory_open, width=11)
        self.button_save.grid(row=4, column=1, sticky="W", padx=10)
        
        
        # buttons to initiate conversion
        st_text = "SimpleGUI > Tkinter Convert!"
        self.button_convert_st = Tkinter.Button(frame, text=st_text, width=40, 
                                                command=self.convert_st)
        self.button_convert_st.grid(row=5, columnspan=2, sticky="S")
        
        ts_text = 'Tkinter > SimpleGUI ... coming "soon"!'
        self.button_convert_ts = Tkinter.Button(frame, text=ts_text, width=40, 
                                                command=None, bg="grey")
        self.button_convert_ts.grid(row=6, columnspan=2, sticky="S")
        
        
        # quit button
        self.button_close = Tkinter.Button(frame, text="Quit", 
                                           command=frame.quit)
        self.button_close.grid(row=7, column=1, sticky="S", pady=5, padx=10)
    
    
    def file_open(self):
        """ open a file dialog to select the file to convert, update automatically 
            contents of "entry_open" and "entry_save" to reflect selected file and 
            proposed an optional name for the output file """
        
        global input_data, input_name
        
        input_loaded = tkFileDialog.askopenfile(title="Choose a file to convert")
        
        if input_loaded:
            # retrieve file data, path, and name
            input_data = input_loaded.read()
            input_path = input_loaded.name
            input_name = self.extract_input_name(input_path)
            input_loaded.close()
            
            # add path of the selected file to "entry_open"
            self.entry_open.delete(0, Tkinter.END)
            self.entry_open.insert(0, input_path)
            
            # add path and optional name of the output file to "entry_save"
            self.entry_save.delete(0, Tkinter.END)
            self.entry_save.insert(0, (input_path[:-3]+"(converted).py"))
    
    
    def directory_open(self):
        """ select or change the destination directory to save the converted file """
        
        dir_save = tkFileDialog.askdirectory(title="Select a destination directory")
        
        if dir_save:
            # add the path and optional name of the output file to "entry_save"
            self.entry_save.delete(0, Tkinter.END)
            self.entry_save.insert(0, (dir_save+"/"+input_name+"(converted).py"))
    
    
    def extract_input_name(self, input_path):
        """ extract the name of a file from the entire file path """
        return re.findall(r'([\w ()-]+)(?:\.py)?$', input_path)[0]
    
    
    def convert_st(self):
        """ handle the conversion from SimpleGUI to Tkinter, and save the result """
        
        # check first if a file was selected and that it contains any data
        if not input_data:
            nofile_text = "Please, select first a file to convert with data in it."
            tkMessageBox.showinfo("No file selected!", message=nofile_text)
            return
        
        # conversion of the input file by calling the Simplegui2Tkinter class
        Simplegui2Tkinter(input_data)
        
        # return an error message if the input file has no SimpleGUI module
        if "___NoSimpleguiFound!___" in output_data:
            error_text = "Wrong file? No SimpleGUI module was found in this file..."
            tkMessageBox.showinfo("Done!", message=error_text)
            return
        
        # save the output file
        test_file = open(self.entry_save.get(), "w")
        test_file.write(output_data)
        test_file.close()
        
        # clear "entry_open" and "entry_save" and signaled user the work is done
        self.entry_open.delete(0, Tkinter.END)
        self.entry_save.delete(0, Tkinter.END)
        
        finished_text = "SUCCESS! Conversion from SimpleGUI to Tkinter finished!"
        tkMessageBox.showinfo("Done!", message=finished_text)



# create the application window
window_root = Tkinter.Tk()
window_root.title("SimpleGUI/Tkinter converter")

app = Window_App(window_root)

# initiate the application window
window_root.mainloop()
