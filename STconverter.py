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


# import global modules
import re
import urllib2 # used by up_music()



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
        self.up_timer()
        self.up_music()
        self.up_key()
        self.up_mouse()
        self.up_ini()
        self.up_color()
    
    
    def up_module(self):
        """ update simplegui module to Tkinter """
        
        global output_data
        
        MODULE_RE = re.compile(r'^(import [\w ,]*)simplegui', re.MULTILINE)
        output_data = MODULE_RE.sub(r'\1Tkinter', input_data)
    
    
    def up_frame_canvas(self):
        """ update the Frame and Canvas widget """
        
        global output_data
        
        sg_frame = "^(\w+) *= *simplegui.create_frame" \
                   "\(([\"\'].+[\"\']), *(\w+), *(\w+),? *(\w+)?\)"
        tk_frame = "window_root = Tkinter.Tk()\n" \
                   "window_root.title(\\2)\n" \
                   "\\1 = Tkinter.Frame(window_root)\n" \
                   "\\1.pack()\n"
        tk_canvas = "w_canvas = Tkinter.Canvas(\\1, width=\\3, height=\\4)\n" \
                    "w_canvas.pack(side='right')\n"
        sg_bg = "\w+.set_canvas_background\([\"\'](\w+)[\"\']\)"
        tk_bg = "w_canvas.configure(background='{}')\n"
        
        FRAME_RE = re.compile(sg_frame, re.MULTILINE)
        
        
        # if no need for Canvas widget, update only the Frame
        if "set_draw_handler" not in output_data:
            output_data = FRAME_RE.sub(tk_frame, output_data)
            return
        
        
        # find name of drawing handler
        draw_handler = re.findall(r'^\w+.set_draw_handler\((.+)\)', output_data, 
                                  re.MULTILINE)[0]
        
        # update drawing handler
        DH_RE = re.compile(r'^def ({n})\(\w+\):\n(\s+)'.format(n=draw_handler), re.MULTILINE)
        output_data = DH_RE.sub(r'def \1():\n\2w_canvas.delete("all")\n\2\n\2', output_data)
        
        # create canvas with size used in "simplegui.create_frame"
        # and with a black background by default
        bg_color = "Black"
        if ".set_canvas_background" in output_data:
            bg_color = re.findall(sg_bg, output_data)[0]
            output_data = re.sub(sg_bg, '', output_data)
        output_data = FRAME_RE.sub(r'{f}\n{c}{b}'.format(f=tk_frame, c=tk_canvas, 
                                    b=tk_bg.format(bg_color)), output_data)
        
        # replace "set_draw_handler" with drawing handler call
        refresh_time = 17 # in ms (66ms~15fps; 33ms~30fps; 17ms~60fps)
        
        dh_old = "\w+.set_draw_handler\({h}\)".format(h=draw_handler)
        dh_new = "def refresh_canvas():\n" \
                 "    {h}()\n" \
                 "    window_root.after({t}, refresh_canvas)\n\n" \
                 "refresh_canvas()\n".format(h=draw_handler, t=refresh_time)
        output_data = re.sub(dh_old, dh_new, output_data)
        
        
        # update Canvas methods
        # Text
        sg_txt = "\w+.draw_text\((.+), ?" \
                 "(\w+|[\[\(][\w ,]+[\]\)]), (\w+), ([\"\']?\w+[\"\']?)\)"
        tk_txt = "w_canvas.create_text(\\2, anchor='sw', " \
                 "text=\\1, font=('DejaVu Serif Condensed', \\3), fill=\\4)"
        output_data = re.sub(sg_txt, tk_txt, output_data)
        
        # Oval
        sg_circle = ".draw_circle\( *(\w+|[\(\[\d, \)\]]+) *, *(\w+|\d+) *, *" \
                    "(\w+|\d+) *, *([\"\']?\w+[\"\']?) *,? *([\"\']?\w*?[\"\']?) *\)"
        tk_oval =     'w_canvas.create_oval(({x1},{y1},{x2},{y2}), width={w}, ' \
                      'outline={l}, fill={f})'
        tk_oval_var = '{v}_x, {v}_y = {v}\n' \
                      '{s}{v}_r = {r}\n' \
                      '{s}{v}_x1, {v}_x2 = ({v}_x - {v}_r), ({v}_x + {v}_r)\n' \
                      '{s}{v}_y1, {v}_y2 = ({v}_y - {v}_r), ({v}_y + {v}_r)\n' \
                      '{s}{n}w_canvas.create_oval(({v}_x1,{v}_y1,{v}_x2,{v}_y2), width={w}, ' \
                      'outline={l}, fill={f})'
        
        ovals = re.findall(sg_circle, output_data)
        
        for oval in ovals:
            is_pos_digit = not re.findall(r"[a-zA-Z]", oval[0])
            is_rad_digit = not re.findall(r"[a-zA-Z]", oval[1])
            
            # if position and radius use digit
            if is_pos_digit and is_rad_digit:
                xy, r, w, l, f = oval
                x, y = re.findall(r"\d+", xy)
                x1, x2 = (int(x) - int(r)), (int(x) + int(r))
                y1, y2 = (int(y) - int(r)), (int(y) + int(r))
                f = f if f else '""'
                output_data = re.sub(r'\w+.draw_circle\( *{xy}.+{r}.+{w}.+{l}.*(?:{f}.+)?\)'.format(
                                                 xy=re.escape(xy), r=r, w=w, l=l, f=f), 
                                     tk_oval.format(x1=x1, y1=y1, x2=x2, y2=y2, w=w, l=l, f=f), 
                                     output_data)
            
            # if position and/or radius is a variable
            else:
                var, r, w, l, f = oval
                name = re.findall(r'(\w+ *= *)?\w+.draw_circle\( *{v}' \
                                   '.+{r}.+{w}.+{l}.*(?:{f}.*)?\)'.format(
                                    v=var, r=r, w=w, l=l, f=f), output_data)
                name = name[0] if name else ''
                space = re.findall(r'( *).+draw_circle\( *{v}' \
                                    '.+{r}.+{w}.+{l}.*(?:{f}.*)?\)'.format(
                                    v=var, r=r, w=w, l=l, f=f), output_data)
                space = space[0] if space else ''
                output_data = re.sub(r'(\w+ *= *)?\w+.draw_circle\( *{v}' \
                                      '.+{r}.+{w}.+{l}.*(?:{f}.*)?\)'.format(
                                      v=var, r=r, w=w, l=l, f=f), 
                                     tk_oval_var.format(v=var, s=space, n=name, r=r, w=w, l=l, f=f), 
                                     output_data)
        
        # Line
        sg_line = "\w+.draw_line\( *([\[\(\w, \*\-\+\/\]\)]+) *, *(\w+)" \
                  " *, *([\"\']?\w+[\"\']?) *\)"
        tk_line = "w_canvas.create_line(\\1, width=\\2, fill=\\3)"
        output_data = re.sub(sg_line, tk_line, output_data)
        
        # Polygon
        sg_poly = "\w+.draw_polygon\( *(\[?[\[\(\w, \]\)]+?\]?) *, *" \
                  "(\w+) *, *([\"\']?\w+[\"\']?) *,? *([\"\']?\w*?[\"\']?) *\)"
        tk_poly = "w_canvas.create_polygon({c}, width={w}, outline={o}, fill={f})"
        polygons = re.findall(sg_poly, output_data)
        for poly in polygons:
            fill = poly[3] if poly[3] else '""'
            output_data = re.sub('\w+.draw_polygon\( *{}.*?\s*?.*?\)'.format(re.escape(poly[0])), 
                                 tk_poly.format(c=poly[0], w=poly[1], o=poly[2], f=fill), 
                                 output_data)
    
    
    def up_button(self):
        """ update Button widget(s) """
        
        global output_data
        
        sg_button = "(?:\w+ ?= ?)?(\w+).add_button\((.+), ?(\w+), ?(\d+)\d\)([ #\w]*)"
        tk_button = "\\3_bt = Tkinter.Button(\\1, text=\\2, command=\\3)\\5\n" \
                    "\\3_bt.config(width=\\4)\n" \
                    "\\3_bt.pack()\n"
        output_data = re.sub(sg_button, tk_button, output_data)
    
    
    def up_label(self):
        """ update Label widget(s) """
        
        global output_data
        
        sg_label =    "(\w+).add_label\((.*)\)" # all with or without variable
        sg_label_nv = "(\w+).add_label\(([\"\'].*[\"\']).*\)" # no variable
        sg_label_wv = "{n} *= *{f}.add_label\({v}\)" # with variable
        tk_label_nv = "Tkinter.Label(\\1, text=\\2).pack()"
        tk_label_wv = "{n}_var = Tkinter.StringVar()\n" \
                      "{n} = Tkinter.Label({f}, textvariable={n}_var).pack()\n" \
                      "{n}_var.set({v})"
        
        # find all labels in order to differentiate the one using text variable
        labels = re.findall(sg_label, output_data)
        
        for label in labels:
            # not using text variable
            if ('"' in label[1] or "'" in label[1]) and "+" not in label[1]:
                output_data = re.sub(sg_label_nv, tk_label_nv, output_data)
            
            # using text variable
            else:
                # get label name
                label_name = re.findall(r"(\w+) *= *{f}.add_label\({v}\)".format(
                                        f=label[0], v=re.escape(label[1])), 
                                        output_data)[0]
                
                # update setting message
                output_data = re.sub(r"{n}.set_text\({v}\)".format(n=label_name, v=re.escape(label[1])), 
                                     r"{n}_var.set({v})".format(n=label_name, v=label[1]), output_data)
                
                # update Label
                output_data = re.sub(sg_label_wv.format(n=label_name, f=label[0], v=re.escape(label[1])), 
                                     tk_label_wv.format(n=label_name, f=label[0], v=label[1]), 
                                     output_data)
    
    
    def up_input(self):
        """ update Entry/Input widget(s) """
        
        global output_data
        
        if "add_input" in output_data:
            
            input_widget = {
            "input_name":    "\w+.add_input\(.+, ?(\w+), ?\d+\)", 
            "param_name":    "^def {n}\((\w+)\):", 
            "handler":       "^def {n}\({p}\):(?:\n .*)+[=( \-+*/]{p}[) \-+*/\n]", 
            "handler_param": "(?<=(?<!{i})[= \(\-+*/]){p}(?=[ \)\-+*/\n])", 
            "sg_input":      "(?:\w+ ?= ?)?(\w+).add_input\((.+), ?(\w+), ?(\d+)\d\)([ #\w]*)", 
            "tk_input":      "\\3_lb = Tkinter.Label(\\1, text=\\2)\\5\n" + \
                             "\\3_lb.pack()\n" + \
                             "\\3_et = Tkinter.Entry(\\1)\n" + \
                             "\\3_et.bind('<Return>', \\3)\n" + \
                             "\\3_et.config(width=\\4)\n" + \
                             "\\3_et.pack()\n"}
            
            # retrieve all Input widgets and respective handler names
            input_names = re.findall(input_widget["input_name"], output_data)
            
            for input_name in input_names:
                # retrieve parameter name used in the Input handler
                param_name = re.findall(input_widget["param_name"].format(n=input_name), 
                                        output_data, re.MULTILINE)[0]
                
                # find and update parameter in the Input handler
                HANDLER_RE = re.compile(input_widget["handler"].format(n=input_name, 
                                        p=param_name), re.MULTILINE)
                
                handler_old = re.findall(HANDLER_RE, output_data)[0]
                handler_new = re.sub(input_widget["handler_param"].format(i=input_name, p=param_name), 
                                     "{}_et.get()".format(input_name), handler_old)
                
                output_data = output_data.replace(handler_old, handler_new)
                
                ## write Tkinter GUI of the Input widget
                INPUT_RE = re.compile(input_widget["sg_input"])
                output_data = INPUT_RE.sub(input_widget["tk_input"], output_data)
    
    
    def up_timer(self):
        """ update timer event """
        
        global output_data
        
        if ".create_timer(" in output_data:
            
            # retrieve all Timer widgets' names
            timer_names = re.findall("(\w+) ?= ?simplegui.create_timer\(", output_data)
            
            for timer_name in timer_names:
                # update timer event handler
                sg_timer_start = "{n}\.start\(\)".format(n=timer_name)
                sg_timer_stop =  "{n}\.stop\(\)".format(n=timer_name)
                tk_timer_start = "{n}_st(True)".format(n=timer_name)
                tk_timer_stop =  "{n}_st(False)".format(n=timer_name)
                output_data = re.sub(sg_timer_start, tk_timer_start, output_data)
                output_data = re.sub(sg_timer_stop, tk_timer_stop, output_data)
                
                # update timer
                sg_timer = "{n} *= *simplegui.create_timer\((\w+), *(\w+)\)".format(n=timer_name)
                tk_timer = "{n}_status = False\n\n" \
                           "def {n}_st(status):\n" \
                           "    global {n}_status\n" \
                           "    {n}_status = status\n\n" \
                           "def {n}_fn():\n" \
                           "    window_root.after(\\1, {n}_fn)\n" \
                           "    if {n}_status:\n" \
                           "        \\2()\n\n" \
                           "{n}_fn()\n".format(n=timer_name)
                output_data = re.sub(sg_timer, tk_timer, output_data)
    
    
    def up_music(self):
        """ update music handler(s) to use pygame module. In case that several 
            musics/sounds are used in the program, the largest music/sound file 
            size will be played with the pygame music module, while others will 
            be considered as sound and played with the sound module """
        
        global output_data
        
        if "simplegui.load_sound" in output_data:
            
            # add pygame (to play the music/sounds) and urllib (to retrieve 
            # music/sounds files over internet) modules to the output data
            output_data = re.sub("(import +.*Tkinter.*\n)", 
                                 "\\1import pygame, urllib\n" + \
                                 "pygame.mixer.init()\n", 
                                 output_data)
            
            
            # update the longest music/sound to use the pygame music module
            
            # find all musics/sounds
            m_all = re.findall("(\w*) *=? *simplegui.load_sound\((.*)\)", output_data)
            
            # verify or find source path to each music/sound
            for m in range(len(m_all)):
                if m_all[m][1][0] not in ["'", '"']:
                    m_all[m] = [m_all[m], re.findall("{m} *= *[\"\'](.*)[\"\']".format(
                                                      m=m_all[m][1]), output_data)[0]]
                else:
                    m_all[m] = [m_all[m], m_all[m][1][1:-1]]
            
            # find longest playing musics/sounds (the largest file size)
            for m in range(len(m_all)):
                m_size = urllib2.urlopen(m_all[m][1]).info().getheaders("Content-Length")[0]
                m_all[m][1] = m_size
            
            m_longest = max(m_all, key=lambda music: int(music[1]))[0]
            
            # update music load, play, pause, rewind, volume
            output_data = re.sub("{n} *=? *simplegui.load_sound\(%s\)".format(n=m_longest), 
                                 "pygame.mixer.music.load(urllib.urlretrieve({u})[0])".format(
                                  u=m_longest[1]), output_data)
            output_data = re.sub("{n}.play\(\)".format(n=m_longest[0]), 
                                 "pygame.mixer.music.play(-1, pygame.mixer.music.get_pos())", output_data)
            output_data = re.sub("{n}.pause\(\)".format(n=m_longest[0]), 
                                 "pygame.mixer.music.pause()", output_data)
            output_data = re.sub("{n}.rewind\(\)".format(n=m_longest[0]), 
                                 "pygame.mixer.music.rewind()", output_data)
            output_data = re.sub("{n}.set_volume\((.*)\)".format(n=m_longest[0]), 
                                 "pygame.mixer.music.set_volume(\\1)", output_data)
            
            
            # update others musics/sounds to use the pygame sound module
            output_data = re.sub("simplegui.load_sound\((.*)\)",
                                 "pygame.mixer.Sound(urllib.urlretrieve(\\1)[0])",
                                 output_data)
    
    
    def up_key(self):
        """ update event handlers involved when a key is pressed or released """
        
        global output_data
        
        
        # event handler when a key is pressed
        
        # find function(s) called by event handler when a key is pressed
        key_pressed = "\w+.set_keydown_handler\((\w+)\)"
        key_pressed_eh_names = re.findall(key_pressed, output_data)
        
        # for each event handler, update event handler and associated function
        for eh_name in key_pressed_eh_names:
            # retrieve parameter name used by event handler
            eh_param = re.findall(r"def {n}\((\w+)\)".format(n=eh_name), output_data)[0]
            # retrieve entire event handler to modify it
            eh_old = re.findall("def {n}\(\w+\):\n(?:    .+\n)+".format(n=eh_name), 
                               output_data)[0]
            # update the capturing of key event
            eh_new = re.sub("chr\(({p})\)".format(p=eh_param), "\\1.keysym", eh_old)
            # update output_data
            output_data = re.sub(re.escape(eh_old), eh_new, output_data)
            
            # update event handler
            output_data = re.sub(r"(\w+).set_keydown_handler\((\w+)\)", 
                                 r'\1.bind("<Key>", \2)\n' \
                                  '\\1.focus_set()\n', 
                                 output_data)
        
        # find function(s) called by event handler when a key is released
        output_data = re.sub(r"(\w+).set_keyup_handler\((\w+)\)",
                             r'\1.bind("<KeyRelease>", \2)\n',
                             output_data)
        
        
        # update other key events
        
        # recognition of a specific pressed key
        keys = re.findall(r"(\w+) ?== ?simplegui.KEY_MAP\[[\"\'](\w+)[\"\']\]", 
                          output_data)
        for key in keys:
            keymap = key[1] if len(key[1]) == 1 else key[1].title()
            output_data = re.sub("{p} ?== ?simplegui.KEY_MAP\[[\"\']{k}[\"\']\]".format(p=key[0], k=key[1]), 
                                 '{p}.keysym == "{k}"'.format(p=key[0], k=keymap),
                                 output_data)
    
    
    def up_mouse(self):
        """ update mouse events """
        
        global output_data
        
        # mouse click
        if "set_mouseclick_handler" in output_data:
            # update function called by set_mouseclick_handler()
            fn_name = re.findall("\w+.set_mouseclick_handler\( *(\w+) *\)", 
                                 output_data)[0]
            output_data = re.sub("( *)def {n}\((\w+)\):\n".format(n=fn_name),
                                 "\\1def {n}(\\2):\n" \
                                 "\\1    \\2 = (\\2.x, \\2.y)\n".format(n=fn_name),
                                 output_data)
            
            # update mouse click event handler registration
            output_data = re.sub("\w+.set_mouseclick_handler\((\w+)\)",
                                 "w_canvas.bind('<Button-1>', \\1)\n",
                                 output_data)
    
    
    def up_ini(self):
        """ update the initialization of the event loop """
        
        global output_data
        
        # if no frame, return
        if "Tkinter.Frame" not in output_data:
            return
        
        frame_name = re.findall(r"(\w+) = Tkinter.Frame\(", output_data)
        START_RE = re.compile(r"{f}.start\(\)".format(f=frame_name[0]))
        output_data = START_RE.sub("", output_data)
        output_data = output_data + "\n\nwindow_root.mainloop()\n"
    
    
    def up_color(self):
        """ some colors used to draw object in SimpleGUI canvas aren't 
            recognized by Tkinter ... try to find a color as close as 
            possible for the colors with known issue """
        
        global output_data
        
        output_data = re.sub(r"[\"\']Lime[\"\']", r"'Lime green'", output_data)
        output_data = re.sub(r"[\"\']Aqua[\"\']", r"'Cyan'", output_data)




########## GUI of the application ##########

# import modules for the GUI
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
