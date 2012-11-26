#!/usr/bin/python


###############################################################################
# SimpleGUI/Tkinter Converter (STconverter) is a little software aiming to 
# convert Python scripts written for SimpleGUI to work with Tkinter GUI instead.
# 
# "Tkinter is Python's de-facto standard GUI (Graphical User Interface) package"
# (http://wiki.python.org/moin/TkInter)
# "SimpleGUI is a custom Python graphical user interface (GUI) module implemented 
# directly in CodeSkulptor that provides an easy to learn interface for building 
# interactive programs in Python" (http://www.codeskulptor.org) used for the 
# online Coursera course "An Introduction to Interactive Programming in Python" 
# by Joe Warren, Scott Rixner, John Greiner, and Stephen Wong (Rice University) 
# 
# For the latest version of STConverter visit the repository on Github: 
# https://github.com/jem-gh/STconverter
# 
# STconverter is developed by Jean-Etienne Morlighem
###############################################################################


# import global modules
import re
import urllib2      # used by up_music()



# SimpleGUI elements' definitions
RNI = {
    # INDENTATION
"I"  : "( *)", 
    # NAME
"N"  : "(\w+)", 
    # NAME OPTIONAL
"No" : "(\w*?)", 
    # CANVAS / FRAME
"C"  : "(\w+)", 
    # PARAMETER: digit, variable, list, operation
"P"  : "([\w\+\-\*\/\%\.\[\(\]\) ]+)", 
    # PARAMETER COORDINATE: digit, variable, list, operation, tuple
"Pc" : "(\w+|[\[\(\w\+\-\*\/\%\. ]+,?[\w\+\-\*\/\%\. \]\)]*)", 
    # PARAMETER MULTILINE: digit, variable, list, operation, tuple, multiline
"Pm" : "([\w\.]+|[\w\.]+[\[\(\w\]\)]+|[\w\+\-\*\/\%\.\[\(\]\)\s,\\\\]+)", 
    # PARAMETER QUOTED: variable, list, quoted string
"Pq" : "((?:[\"].*?[\"]|[\'].*?[\']|[\w\.]+|[\w\.]+[\[\(\w\]\)]+|[\w\+\-\*\/\%\.\[\(\]\) ]+)+?)", 
    # SPACE: comma, space, \n, \
"S"  : "(?: *,[\s\\\]*)", 
    # COMMENT
"M"  : "( *#?.*)"
}



class Simplegui2Tkinter:
    """ update SimpleGUI parts to Tkinter """
    
    def __init__(self, code_input):
        self.code = code_input
    
    
    def convert(self):
        """ call other methods to update each SimpleGUI parts to Tkinter """
        
        # stop conversion if the input code do not use the simplegui module
        if not "simplegui" in self.code:
            return "___NoSimpleguiFound!___"
        
        self.up_module()
        self.up_frame_canvas()
        self.up_canvas_text()
        self.up_canvas_oval()
        self.up_canvas_line()
        self.up_canvas_polyline()
        self.up_canvas_polygon()
        self.up_button()
        self.up_label()
        self.up_input()
        self.up_timer()
        self.up_music()
        self.up_image()
        self.up_key()
        self.up_mouse()
        self.up_ini()
        self.up_Tkinter_incompatible()
        
        # return converted code
        return self.code
    
    
    def up_module(self):
        """ update simplegui module to Tkinter and add division from future """
        
        # update simplegui module to Tkinter
        self.code = re.sub("(import [\w ,]*)simplegui", 
                           "\\1Tkinter", 
                           self.code)
        
        # add division from future to enable true division in Python 2.7
        self.code = re.sub("^((?:\s|(?:#.*\n))*)", 
                           "\\1\nfrom __future__ import division\n\n", 
                           self.code)
    
    
    def up_frame_canvas(self):
        """ update the Frame and Canvas widget """
        
        sg_frame = "{I}{N} *= *simplegui.create_frame" \
                   "\( *{Pq}{S}{P}{S}{P}{S}?{P}? *\){M}".\
                   format(I=RNI["I"], N=RNI["N"], Pq=RNI["Pq"], 
                          S=RNI["S"], P=RNI["P"], M=RNI["M"])
        tk_frame = "\\1window_root = Tkinter.Tk()\\7\n" \
                   "\\1window_root.title(\\3)\n" \
                   "\\1\\2 = Tkinter.Frame(window_root)\n" \
                   "\\1\\2.pack()\n"
        
        tk_canvas = "\\1canvas = Tkinter.Canvas(\\2, width=\\4, height=\\5)\n" \
                    "\\1canvas.pack(side='right')\n"
        
        sg_bg = "\w+.set_canvas_background\( *{Pq} *\){M}".\
                format(Pq=RNI["Pq"], M=RNI["M"])
        tk_bg = "\\1canvas.configure(background={b}){m}\n"
        
        FRAME_RE = re.compile(sg_frame)
        
        # if no need for Canvas widget, update only the Frame
        if "set_draw_handler" not in self.code:
            self.code = FRAME_RE.sub(tk_frame, self.code)
            return
        
        
        # update drawing handler
        sg_drawing_handler = "{I}def {n}\( *{N} *\):\n"
        tk_drawing_handler = "\\1def {n}(\\2):\n" \
                             "\\1    \\2.delete('all')\n" \
                             "\\1    \n"
        
        draw_n = re.findall('\w+.set_draw_handler\( *{N} *\)'.format(N=RNI["N"]), 
                            self.code)[0]
        self.code = re.sub(sg_drawing_handler.format(I=RNI["I"], n=draw_n, 
                               N=RNI["N"]), 
                           tk_drawing_handler.format(n=draw_n), 
                           self.code)
        
        # create canvas with size used in "simplegui.create_frame"
        # and with a black background by default
        bg = ("'Black'", "")
        if ".set_canvas_background" in self.code:
            bg = re.findall(sg_bg, self.code)[0]
            self.code = re.sub(sg_bg, '', self.code)
        self.code = FRAME_RE.sub(r'{f}\n{c}{b}'.format(f=tk_frame, c=tk_canvas, 
                                     b=tk_bg.format(b=bg[0], m=bg[1])), 
                                 self.code)
        
        # replace "set_draw_handler" with drawing handler call
        refresh_time = 17 # in ms (66ms~15fps; 33ms~30fps; 17ms~60fps)
        
        dh_old = "{I}\w+.set_draw_handler\( *{h} *\){M}".format(
                     I=RNI["I"], h=draw_n, M=RNI["M"])
        dh_new = "\\1def refresh_canvas():\\2\n" \
                 "\\1    {h}(canvas)\n" \
                 "\\1    window_root.after({t}, refresh_canvas)\n\n" \
                 "\\1refresh_canvas()\n".format(h=draw_n, t=refresh_time)
        self.code = re.sub(dh_old, dh_new, self.code)
    
    
    def up_canvas_text(self):
        """ update the Canvas text item(s) """
        
        sg_txt = "{C}.draw_text\( *{Pq}{S}{Pc}{S}{P}{S}{Pq} *\)".\
                 format(C=RNI["C"], Pq=RNI["Pq"], S=RNI["S"], Pc=RNI["Pc"], 
                        P=RNI["P"])
        tk_txt = "\\1.create_text(\\3, anchor='sw', " \
                 "text=\\2, font=('DejaVu Serif Condensed', \\4), fill=\\5)"
        self.code = re.sub(sg_txt, tk_txt, self.code)
    
    
    def up_canvas_oval(self):
        """ update the Canvas circle/oval item(s) """
        
        # return if no circle/oval defined in input code
        if "draw_circle" not in self.code:
            return
        
        sg_circle = "{No} *=? *{C}.draw_circle" \
                    "\( *{Pm}{S}{P}{S}{P}{S}{Pq}{S}?{Pq}? *\)".\
                    format(No=RNI["No"], C=RNI["C"], Pm=RNI["Pm"], 
                           S=RNI["S"], P=RNI["P"], Pq=RNI["Pq"])
        tk_oval     = '{c}.create_oval(({x1},{y1},{x2},{y2}), width={w}, ' \
                          'outline={l}, fill={f})'
        tk_oval_var = '\\1coor = STconverter_oval({coor}, {r})\n' \
                      '\\1{n}{c}.create_oval(coor, width={w}, ' \
                          'outline={l}, fill={f})'
        # function added to the converted file to calculate oval(s) coordinates 
        # if position and/or radius is a variable (not installed by default)
        fn = "def STconverter_oval(xy, r):\n" \
             "    x, y = xy\n" \
             "    return ((x - r), (y - r), (x + r), (y + r))\n\n"
        fn_needed = False
        
        ovals = re.findall(sg_circle, self.code)
        
        for oval in ovals:
            n, c, coor, r, w, l, f = oval
            fill = f if f else '""'
            
            # if coor and r use digit only, without variables nor operations
            is_pos_digit = not re.findall(r"[a-zA-Z\+\-\*\/\%]", coor)
            is_rad_digit = not re.findall(r"[a-zA-Z\+\-\*\/\%]", r)
            if is_pos_digit and is_rad_digit:
                x, y = re.findall(r"\d+", coor)
                x1, x2 = (int(x) - int(r)), (int(x) + int(r))
                y1, y2 = (int(y) - int(r)), (int(y) + int(r))
                self.code = re.sub("{c}.draw_circle\( *" \
                                   "{coor}{S}{r}{S}{w}{S}{l}{S}?{f} *\)".\
                                   format(c=c, coor=re.escape(coor), S=RNI["S"], 
                                       r=r, w=re.escape(w), l=re.escape(l), 
                                       f=re.escape(f)), 
                                   tk_oval.format(c=c, x1=x1, y1=y1, x2=x2, 
                                       y2=y2, w=w, l=l, f=fill), 
                                   self.code)
            
            # if position and/or radius is a variable
            else:
                fn_needed = True
                name = n + " = " if n else ''
                self.code = re.sub("{I}{n} *=? *{c}.draw_circle\( *" \
                                   "{coor}{S}{r}{S}{w}{S}{l}{S}?{f} *\)".\
                                   format(I=RNI["I"], n=n, c=c, 
                                       coor=re.escape(coor), S=RNI["S"], 
                                       r=re.escape(r), w=re.escape(w), 
                                       l=re.escape(l), f=re.escape(f)), 
                                   tk_oval_var.format(coor=coor, r=r, n=name, 
                                       c=c, w=w, l=l, f=fill), 
                                   self.code)
        
        # add fn to the converted code if needed 
        if fn_needed:
            last = re.findall("^((?:import +.+\n)|(?:from +.+\n))", 
                              self.code, re.M)[-1]
            self.code = re.sub(last, "{m}\n".format(m=last) + fn, self.code)
    
    
    def up_canvas_line(self):
        """ update the Canvas line item(s) """
        
        sg_line = "{C}.draw_line\( *{Pc}{S}{Pc}{S}{P}{S}{Pq} *\)".\
                  format(C=RNI["C"], Pc=RNI["Pc"], S=RNI["S"], P=RNI["P"], 
                         Pq=RNI["Pq"])
        tk_line = "\\1.create_line(\\2, \\3, width=\\4, fill=\\5)"
        self.code = re.sub(sg_line, tk_line, self.code)
    
    
    def up_canvas_polyline(self):
        """ update the Canvas polyline item(s) """
        
        sg_pline = "{C}.draw_polyline\( *{Pm}{S}{P}{S}{Pq} *\)"
        tk_pline = "{c}.create_line({coor}, width={w}, fill={f})"
        
        polylines = re.findall(sg_pline.format(C=RNI["C"], Pm=RNI["Pm"], 
                                   S=RNI["S"], P=RNI["P"], Pq=RNI["Pq"]), 
                               self.code)
        
        for p in polylines:
            # if coor is a variable, repeat the first point to avoid a crash 
            # of the converted program in case the variable only has one point
            is_coor_var = re.findall(r"^\w+", p[1])
            coor = p[1] if not is_coor_var else p[1] + "[0], " + p[1]
            self.code = re.sub(sg_pline.format(C=p[0], Pm=re.escape(p[1]), S=RNI["S"], 
                                   P=re.escape(p[2]), Pq=re.escape(p[3])), 
                               tk_pline.format(c=p[0], coor=coor, w=p[2], f=p[3]), 
                               self.code)
    
    
    def up_canvas_polygon(self):
        """ update the Canvas polygon item(s) """
        
        sg_poly = "{C}.draw_polygon\( *{Pm}{S}{P}{S}{Pq}{S}?{Pq}? *\)".\
                  format(C=RNI["C"], Pm=RNI["Pm"], S=RNI["S"], P=RNI["P"], 
                         Pq=RNI["Pq"])
        tk_poly = "{n}.create_polygon({c}, width={w}, outline={o}, fill={f})"
        polygons = re.findall(sg_poly, self.code)
        for p in polygons:
            fill = p[4] if p[4] else '""'
            self.code = re.sub('{n}.draw_polygon\( *{a}{S}{w}{S}{c}{S}?{f} *\)'.\
                               format(n=p[0], a=re.escape(p[1]), S=RNI["S"], 
                                   w=re.escape(p[2]), c=re.escape(p[3]), 
                                   f=re.escape(p[4])), 
                               tk_poly.format(n=p[0], c=p[1], w=p[2], o=p[3], 
                                   f=fill), 
                               self.code)
    
    
    def up_button(self):
        """ update Button widget(s) """
        
        sg_button = "{C}.add_button\( *{Pq}{S}{N}{S}?{P}? *\){M}".\
                    format(C=RNI["C"], Pq=RNI["Pq"], S=RNI["S"], N=RNI["N"], 
                           P=RNI["P"], M=RNI["M"])
        sg_b_ch =   "{I}(?:\w+ *= *)?{f}.add_button\( *{m}{S}{h}{S}?{s} *\){M}"
        tk_b_ws = "\\1{h}_bt = Tkinter.Button({f}, text={m}, command={h})\\2\n" \
                  "\\1{h}_bt.config(width={s})\n" \
                  "\\1{h}_bt.pack()\n"
        tk_b_ns = "\\1{h}_bt = Tkinter.Button({f}, text={m}, command={h})\\2\n" \
                  "\\1{h}_bt.pack()\n"
        
        buttons = re.findall(sg_button, self.code)
        
        for button in buttons:
            # decrease by a factor 10 the button size (if any) to fit Tkinter 
            size = button[3] if button[3] else ''
            is_size_digit = not re.findall(r"[a-zA-Z\+\-\*\/\%]", size)
            if size and is_size_digit:
                size = int(size) / 10
            
            if size:
                self.code = re.sub(sg_b_ch.format(I=RNI["I"], f=button[0], 
                                       m=re.escape(button[1]), S=RNI["S"], 
                                       h=button[2], s=re.escape(button[3]), 
                                       M=RNI["M"]),
                                   tk_b_ws.format(f=button[0], m=button[1], 
                                       h=button[2], s=size), 
                                   self.code)
            elif not size:
                self.code = re.sub(sg_b_ch.format(I=RNI["I"], f=button[0], 
                                       m=re.escape(button[1]), S=RNI["S"], 
                                       h=button[2], s=re.escape(button[3]), 
                                       M=RNI["M"]),
                                   tk_b_ns.format(f=button[0], m=button[1], 
                                       h=button[2]), 
                                   self.code)
    
    
    def up_label(self):
        """ update Label widget(s) """
        
        sg_label =    "{No} *=? *{C}.add_label\( *{Pq}{S}?{P}? *\){M}\n".\
                      format(No=RNI["No"], C=RNI["C"], Pq=RNI["Pq"], 
                             S=RNI["S"], P=RNI["P"], M=RNI["M"])
        sg_label_nv  = "{I}{n} *=? *{f}.add_label\( *{m}{S}?{s} *\)"
        sg_label_wv  = "{I}{n} *= *{f}.add_label\( *{m}{S}?{s} *\)"
        tk_label_nv = "\\1Tkinter.Label({f}, text={m}).pack()"
        tk_label_wv = "\\1{n}_var = Tkinter.StringVar()\n" \
                      "\\1{n} = Tkinter.Label({f}, textvariable={n}_var).pack()\n" \
                      "\\1{n}_var.set({m})"
        
        # find all labels in order to differentiate the ones using text variable
        labels = re.findall(sg_label, self.code)
        
        for l in labels:
            # not using text variable
            if ("\n{n}.set_text".format(n=l[0]) and 
                " {n}.set_text".format(n=l[0])) not in self.code:
                self.code = re.sub(sg_label_nv.format(I=RNI["I"], n=l[0], 
                                       f=l[1], S=RNI["S"], m=re.escape(l[2]), 
                                       s=re.escape(l[3])), 
                                   tk_label_nv.format(f=l[1], m=l[2]), 
                                   self.code)
            
            # using text variable
            else:
                # update setting message
                self.code = re.sub("([\n ]){n}.set_text\(".format(n=l[0]), 
                                   "\\1{n}_var.set(".format(n=l[0]), 
                                   self.code)
                # update Label
                self.code = re.sub(sg_label_wv.format(I=RNI["I"], n=l[0], 
                                       f=l[1], S=RNI["S"], m=re.escape(l[2]), 
                                       s=re.escape(l[3])), 
                                   tk_label_wv.format(n=l[0], f=l[1], m=l[2]), 
                                   self.code)
    
    
    def up_input(self):
        """ update Entry/Input widget(s) """
        
        # return if no input field defined in input code
        if "add_input" not in self.code:
            return
        
        sg_input = "{I}{No} *=? *{C}.add_input\( *{Pq}{S}{N}{S}{P} *\){M}"
        tk_input = "{i}{n}_lb = Tkinter.Label({f}, text={l})\\1\n" \
                   "{i}{n}_lb.pack()\n" \
                   "{i}{n}_et = Tkinter.Entry({f})\n" \
                   "{i}{n}_et.bind('<Return>', {n})\n" \
                   "{i}{n}_et.config(width={s})\n" \
                   "{i}{n}_et.pack()\n"
        sg_inp_fn_p = "def {n}\( *{N} *\):"
        sg_inp_fn   = "def {n}\( *{p} *\): *(?:\n .*)+[=( \-+*/]{p}[) \-+*/\n]"
        param_def   = "(?<=(?<!{i})[= \(\-+*/]){p}(?=[ \)\.\-+*/\n])"
        
        inputs = re.findall(sg_input.format(I=RNI["I"], No=RNI["No"], C=RNI["C"], 
                                Pq=RNI["Pq"], S=RNI["S"], N=RNI["N"], P=RNI["P"], 
                                M=RNI["M"]), 
                            self.code)
        
        for i in inputs:
            # retrieve parameter name used in the Input handler
            p = re.findall(sg_inp_fn_p.format(n=i[4], N=RNI["N"]), self.code)[0]
            
            # find and update parameter in the Input handler
            handler_old = re.findall(sg_inp_fn.format(n=i[4], p=p), 
                                     self.code)[0]
            handler_new = re.sub(param_def.format(i=i[4], p=p), 
                                 "{}_et.get()".format(i[4]), 
                                 handler_old)
            self.code = self.code.replace(handler_old, handler_new)
            
            ## write Tkinter GUI of the Input widget
            tk_input_size = "int(" + i[5] + "/10)"
            self.code = re.sub(sg_input.format(I=i[0], No=i[1], C=i[2], 
                                   Pq=re.escape(i[3]), S=RNI["S"], N=i[4], 
                                   P=re.escape(i[5]), M=RNI["M"]), 
                               tk_input.format(i=i[0], n=i[4], f=i[2], l=i[3], 
                                   s=tk_input_size), 
                               self.code)
    
    
    def up_timer(self):
        """ update timer event """
        
        # return if no timer defined in input code
        if "create_timer" not in self.code:
            return
        
        # add a class to handle all timers at the beginning of the converted 
        # file just after the imported modules 
        cl = "class STconverter_timer:\n" \
             "    def __init__(self, interval, function):\n" \
             "        self.interval = int(interval)\n" \
             "        self.function = function\n" \
             "        self.status = False\n" \
             "    \n" \
             "    def set_status(self, status):\n" \
             "        if status != self.status:\n" \
             "            self.status = status\n" \
             "            self.run()\n" \
             "    \n" \
             "    def run(self):\n" \
             "        if self.status:\n" \
             "            window_root.after(self.interval, self.run)\n" \
             "            self.function()\n\n"
        
        last = re.findall("^((?:import +.+\n)|(?:from +.+\n))", 
                          self.code, re.M)[-1]
        self.code = re.sub(last, "{m}\n".format(m=last) + cl, self.code)
        
        # retrieve all Timer widgets' names
        timer_names = re.findall("{N} *= *simplegui.create_timer\(".format(
                                     N=RNI["N"]), 
                                 self.code)
        
        for t in timer_names:
            # update timer event handler(s)
            sg_timer_start = "{}\.start\(\)".format(t)
            sg_timer_stop =  "{}\.stop\(\)".format(t)
            tk_timer_start = "{}.set_status(True)".format(t)
            tk_timer_stop =  "{}.set_status(False)".format(t)
            self.code = re.sub(sg_timer_start, tk_timer_start, self.code)
            self.code = re.sub(sg_timer_stop, tk_timer_stop, self.code)
            
            # update timer(s)
            sg_timer = "{I}{t} *= *simplegui.create_timer" \
                       "\( *{P}{S}{N} *\){M}"
            tk_timer = "\\1{t} = STconverter_timer(\\2, \\3)\\4"
            self.code = re.sub(sg_timer.format(I=RNI["I"], t=t, P=RNI["P"], 
                                   S=RNI["S"], N=RNI["N"], M=RNI["M"]), 
                               tk_timer.format(t=t), 
                               self.code)
    
     
    def up_music(self):
        """ update music handler(s) to use pygame module. In case that several 
            musics/sounds are used in the program, the largest music/sound file 
            size will be played with the pygame music module, while others will 
            be considered as sound and played with the sound module """
        
        # return if no music/sound defined in input code
        if "simplegui.load_sound" not in self.code:
            return
        
        # add pygame (to play the music/sounds) and urllib (to retrieve 
        # music/sounds files over internet) modules to the output data
        self.code = re.sub("(import +.*Tkinter.*\n)", 
                           "\\1import pygame, urllib\n" + \
                           "pygame.mixer.init()\n", 
                           self.code)
        
        
        # update the longest music/sound to use the pygame music module
        
        # find all musics/sounds
        m_all = re.findall("{No} *=? *simplegui.load_sound\( *{Pq} *\)".\
                               format(No=RNI["No"], Pq=RNI["Pq"]), 
                           self.code)
        
        # verify or find source path of each music/sound
        for m in range(len(m_all)):
            if m_all[m][1][0] not in ["'", '"']:
                # if the link is in a list
                if "[" in m_all[m][1]:
                    ref = re.findall("\w+", m_all[m][1])
                    l = re.findall("{l} *= *\[\s*{Pq}+\s*\]".format(l=ref[0], 
                                       Pq=RNI["Pq"], S=RNI["S"]), 
                                   self.code, re.S)
                    l = re.split(" *, *\n? *", l[0])[int(ref[1])][1:-1]
                    m_all[m] = [m_all[m], l]
                
                # if the link is the value of a variable
                elif "[" not in m_all[m][1]:
                    m_all[m] = [m_all[m], re.findall("{m} *= *{Pq}".format(
                                    m=m_all[m][1], Pq=RNI["Pq"]), 
                                self.code)[0][1:-1]]
            else:
                m_all[m] = [m_all[m], m_all[m][1][1:-1]]
        
        # find longest playing musics/sounds (the largest file size)
        for m in range(len(m_all)):
            m_size = urllib2.urlopen(
                         m_all[m][1]).info().getheaders("Content-Length")[0]
            m_all[m][1] = m_size
        
        m_longest = max(m_all, key=lambda music: int(music[1]))
        
        # if the size seems reasonable to be a music and not a sound
        if int(m_longest[1]) >= 500000:
            m = m_longest[0]
            # update music load, play, pause, rewind, volume
            sg_load = "{n} *=? *simplegui.load_sound\( *{u} *\)".format(
                          n=m[0], u=m[1])
            tk_load = "pygame.mixer.music.load(urllib.urlretrieve({u})[0])".\
                          format(u=m[1])
            self.code = re.sub(sg_load, tk_load, self.code)
            sg_play = "{n}.play\(\)".format(n=m[0])
            tk_play = "pygame.mixer.music.play(-1, pygame.mixer.music.get_pos())"
            self.code = re.sub(sg_play, tk_play, self.code)
            sg_pause = "{n}.pause\(\)".format(n=m[0])
            tk_pause = "pygame.mixer.music.pause()"
            self.code = re.sub(sg_pause, tk_pause, self.code)
            sg_rewind = "{n}.rewind\(\)".format(n=m[0])
            tk_rewind = "pygame.mixer.music.rewind()"
            self.code = re.sub(sg_rewind, tk_rewind, self.code)
            sg_vol = "{n}.set_volume\((.*)\)".format(n=m[0])
            tk_vol = "pygame.mixer.music.set_volume(\\1)"
            self.code = re.sub(sg_vol, tk_vol, self.code)
        
        
        # update others musics/sounds to use the pygame sound module
        self.code = re.sub("simplegui.load_sound\((.*)\)",
                           "pygame.mixer.Sound(urllib.urlretrieve(\\1)[0])",
                           self.code)
    
    
    def up_image(self):
        """ update images using the Python Imaging Library (PIL) with ImageTk """
        
        # return if no image used in input code
        if "draw_image" not in self.code:
            return
        
        # add Python Imaging Library (PIL) (to process images) and urllib module 
        # (to retrieve images from Internet) if not yet available
        m_tk =  "(import +.*Tkinter.*\n)"
        m_url = "(import +.*urllib.*\n)"
        n_url = "\\1import urllib\n" \
                "from PIL import Image, ImageTk\n\n"
        w_url = "\\1from PIL import Image, ImageTk\n\n\n"
        
        # Class added to the converted file if images are used in the program. 
        # The class will store, process, and draw images and the parts/tiles 
        # derived from them in a Tkinter-compatible manner, with: 
        # image = source image retrieved from Internet 
        # s_coor, s_size = coordinates (x, y) and size (width, height) 
        #                  in pixels of a selection of the source image 
        # d_coor, d_size = coordinates (x, y) and size (width, height) 
        #                  in pixels of the selected part of the image 
        #                  on the canvas 
        # a = angle in radians of clockwise rotation around its center 
        # c = canvas
        cl = "class STconverter_image:\n" \
             "    def __init__(self, image):\n" \
             "        self.img = image\n" \
             "        self.tiles = {}\n" \
             "    \n" \
             "    def update(self, s_coor, s_size, d_size, d, ID):\n" \
             "        x1, y1 = (s_coor[0]-s_size[0]/2), (s_coor[1]-s_size[1]/2)\n" \
             "        x2, y2 = (s_coor[0]+s_size[0]/2), (s_coor[1]+s_size[1]/2)\n" \
             "        processed = self.img.crop((int(x1), int(y1), int(x2), int(y2)))\n" \
             "        if d_size != s_size:\n" \
             "            processed = processed.resize(d_size, resample=Image.BILINEAR)\n" \
             "        if d:\n" \
             "            processed = processed.rotate(-d, resample=Image.BICUBIC, expand=1)\n" \
             "        self.tiles[ID] = ImageTk.PhotoImage(processed)\n" \
             "    \n" \
             "    def create_ID(self, params):\n" \
             "        return ','.join(str(param) for param in params)\n" \
             "    \n" \
             "    def draw(self, c, s_coor, s_size, d_coor, d_size, a):\n" \
             "        d = int((a * 180 / 3.1416) % 360)\n" \
             "        ID = self.create_ID([s_coor, s_size, d_coor, d_size, d])\n" \
             "        if ID not in self.tiles:\n" \
             "            self.update(s_coor, s_size, d_size, d, ID)\n" \
             "        canvas.create_image(d_coor, image=self.tiles[ID])\n\n"
        
        if "urllib" in self.code:
            self.code = re.sub(m_url, w_url + cl, self.code)
        else:
            self.code = re.sub(m_tk, n_url + cl, self.code)
        
        
        # update all images loading
        self.code = re.sub("{N} *=? *simplegui.load_image\( *{Pq} *\)".\
                               format(N=RNI["N"], Pq=RNI["Pq"]), 
                           "\\1 = STconverter_image(Image.open(" \
                                                   "urllib.urlretrieve(\\2)[0]))", 
                           self.code)
        
        
        # update all images drawing
        sg_image = "{N}.draw_image\( *{N}{S}{Pc}{S}{Pc}{S}{Pc}{S}{Pc}{S}?{P}? *\){M}"
        sg_img_c = "{c}.draw_image\( *{n}{S}{sc}{S}{ss}{S}{dc}{S}{ds}{S}?{a}? *\){M}"
        tk_image = "{n}.draw({c}, {sc}, {ss}, {dc}, {ds}, {a})\\1\n"
        
        images = re.findall(sg_image.format(N=RNI["N"], S=RNI["S"], Pc=RNI["Pc"], 
                                P=RNI["P"], M=RNI["M"]), 
                            self.code)
        
        for i in images:
            angle = i[6] if i[6] else 0
            self.code = re.sub(sg_img_c.format(c=i[0], n=i[1], sc=re.escape(i[2]), 
                                   ss=re.escape(i[3]), dc=re.escape(i[4]), 
                                   ds=re.escape(i[5]), a=re.escape(i[6]), 
                                   S=RNI["S"], M=RNI["M"]), 
                               tk_image.format(n=i[1], c=i[0], sc=i[2], ss=i[3], 
                                   dc=i[4], ds=i[5], a=angle), 
                               self.code)
    
    
    def up_key(self):
        """ update event handlers involved when a key is pressed or released """
        
        # find and update each pressed-key call to handler and handler
        sg_k_down = "{I}{C}.set_keydown_handler\( *{N} *\){M}"
        tk_k_down = '\\1{c}.bind("<Key>", {e}){m}\n' \
                    '\\1{c}.focus_set()\n'
        
        k_down = re.findall(sg_k_down.format(I=RNI["I"], C=RNI["C"], N=RNI["N"], 
                                M=RNI["M"]), 
                            self.code)
        for eh in k_down:
            # retrieve parameter name used by event handler
            eh_param = re.findall("def {e}\( *{N} *\)".format(e=eh[2], N=RNI["N"]), 
                                  self.code)[0]
            # retrieve entire event handler to update the capturing of key event
            eh_old = re.findall(" *def {e}\( *{p} *\):.*\n" \
                                "(?: *.+\n)+".format(e=eh[2], p=eh_param), 
                                self.code)[0]
            eh_new = re.sub("chr\( *({p}) *\)".format(p=eh_param), 
                            "\\1.keysym", 
                            eh_old)
            # update event handler
            self.code = re.sub(re.escape(eh_old), eh_new, self.code)
            # update call to handler
            self.code = re.sub(sg_k_down.format(I=RNI["I"], C=eh[1], N=eh[2], 
                                   M=re.escape(eh[3])), 
                               tk_k_down.format(c=eh[1], e=eh[2], m=eh[3]), 
                               self.code)
        
        # find and update each released-key call to event handler
        sg_k_up = "{C}.set_keyup_handler\( *{N} *\){M}".format(
                      C=RNI["C"], N=RNI["N"], M=RNI["M"])
        tk_k_up = '\\1.bind("<KeyRelease>", \\2)\\3\n'
        self.code = re.sub(sg_k_up, tk_k_up, self.code)
        
        
        # update other key events
        
        # recognition of a specific pressed key
        sg_k_spe = "{N} *== *simplegui.KEY_MAP\[{Pq}\]"
        tk_k_spe = '{p}.keysym == "{k}"'
        
        keys = re.findall(sg_k_spe.format(N=RNI["N"], Pq=RNI["Pq"]), self.code)
        
        for k in keys:
            keymap = k[1][1:-1] if len(k[1][1:-1]) == 1 else k[1][1:-1].title()
            self.code = re.sub(sg_k_spe.format(N=k[0], Pq=k[1]), 
                               tk_k_spe.format(p=k[0], k=keymap),
                               self.code)
    
    
    def up_mouse(self):
        """ update mouse events """
        
        # mouse click
        if "set_mouseclick_handler" in self.code:
            
            sg_click = "{C}.set_mouseclick_handler\( *{N} *\){M}".format(
                           C=RNI["C"], N=RNI["N"], M=RNI["M"])
            tk_click = "canvas.bind('<Button-1>', \\2)\\3\n"
            
            # update function called by set_mouseclick_handler()
            fn_name = re.findall(sg_click, self.code)[0][1]
            self.code = re.sub("{I}def {n}\( *{N} *\):\n".format(I=RNI["I"], 
                                   n=fn_name, N=RNI["N"]), 
                               "\\1def {n}(\\2):\n" \
                               "\\1    if isinstance(\\2, Tkinter.Event):\n" \
                               "\\1        \\2 = (\\2.x, \\2.y)\n".format(
                                   n=fn_name), 
                               self.code)
            
            # update mouse click event handler registration
            self.code = re.sub(sg_click, tk_click, self.code)
    
    
    def up_ini(self):
        """ update the initialization of the window event loop """
        
        # if no frame, return
        if "Tkinter.Frame" not in self.code:
            return
        
        frame = re.findall("{N} = Tkinter.Frame\(".format(N=RNI["N"]), 
                           self.code)[0]
        self.code = re.sub("{f}.start\(\){M}".format(f=frame, M=RNI["M"]), 
                           "", 
                           self.code)
        self.code = self.code + "\n\nwindow_root.mainloop()\n"
    
    
    def up_Tkinter_incompatible(self):
        
        """ some color names specified to draw object in SimpleGUI canvas 
            aren't always well recognized by Tkinter ... change to their 
            RGB value """
        self.code = re.sub(r"[\"\'][aA]qua[\"\']", r"'#00FFFF'", self.code)
        self.code = re.sub(r"[\"\'][fF]uchsia[\"\']", r"'#FF00FF'", self.code)
        self.code = re.sub(r"[\"\'][lL]ime[\"\']", r"'#00FF00'", self.code)
        self.code = re.sub(r"[\"\'][oO]live[\"\']", r"'#808000'", self.code)
        self.code = re.sub(r"[\"\'][sS]ilver[\"\']", r"'#C0C0C0'", self.code)
        self.code = re.sub(r"[\"\'][tT]eal[\"\']", r"'#008080'", self.code)
        
        """ SimpleGUI handles doc strings ending with four double quotes 
            which is not always well handled by other Python interpreters """
        self.code = re.sub('""""', '"""', self.code)




########## GUI of the application ##########

# import modules for the GUI
import Tkinter, tkFileDialog, tkMessageBox


class Window_App:
    def __init__(self, master):
        self.master = master
        
        self.input_data = ""
        self.input_path = ""
        self.input_filename = ""
        
        self.output_path = ""
        self.output_filename = ""
        
        self.isWindows = False
        
        self.main()
    
    
    def main(self):
        """ core of the application GUI """
        
        # Frame
        frame = Tkinter.Frame(self.master)
        frame.grid()
        frame.rowconfigure(0, minsize=40)
        frame.rowconfigure(3, minsize=40)
        frame.rowconfigure(5, minsize=60)
        frame.rowconfigure(6, minsize=60)
        
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
        
        
        # button to initiate conversion
        st_text = "SimpleGUI > Tkinter Convert!"
        self.button_convert_st = Tkinter.Button(frame, text=st_text, width=40, 
                                                command=self.convert_st)
        self.button_convert_st.grid(row=5, columnspan=2, sticky="S")
        
        
        # quit button
        self.button_close = Tkinter.Button(frame, text="Quit", 
                                           command=frame.quit)
        self.button_close.grid(row=6, column=1, sticky="S", pady=5, padx=10)
    
    
    def file_open(self):
        """ open a file dialog to select the file to convert, update automatically 
            contents of "entry_open" with the selected file and "entry_save" with 
            a default name for the output file """
        
        input_loaded = tkFileDialog.askopenfile(title="Choose a file to convert")
        
        if input_loaded:
            # retrieve input file data, path, and name
            self.input_data = input_loaded.read()
            self.input_path, self.input_filename = self.pathNfilename(
                                                            input_loaded.name)
            input_loaded.close()
            
            # create a default output file path and name
            self.output_path = self.input_path
            self.output_filename = self.update_name(self.input_filename, ".py", 
                                                    tag="(converted)")
            
            # add path of the selected file to "entry_open"
            self.entry_open.delete(0, Tkinter.END)
            self.entry_open.insert(0, self.input_path + self.input_filename)
            
            # add path and name of the output file to "entry_save"
            self.entry_save.delete(0, Tkinter.END)
            self.entry_save.insert(0, (self.output_path + self.output_filename))
    
    
    def directory_open(self):
        """ select or change the destination directory of the output file """
        
        d = tkFileDialog.askdirectory(title="Select a destination directory")
        if d:
            # update the path of the output file to "entry_save"
            div = "/" if not self.isWindows else "\\"
            self.output_path = d + div
            self.entry_save.delete(0, Tkinter.END)
            self.entry_save.insert(0, (self.output_path + self.output_filename))
    
    
    def pathNfilename(self, full_path):
        """ separate and return the path and the filename from a full path """
        
        # on Linux and Mac OS
        if "/" in full_path:
            return re.findall(r"(.*/)(.+)", full_path)[0]
        # on Windows
        if "\\" in full_path:
            self.isWindows = True
            return re.findall(r"(.*\\)(.+)", full_path)[0]
    
    
    def update_name(self, filename, extension, tag=""):
        """ verify that a filename use the correct extension (otherwise add it) 
            and, if specified, insert a tag between the name and the extension """
        
        if filename[-len(extension):] == extension:
            return filename[:-len(extension)] + tag + extension
        
        else:
            return filename + tag + extension
    
    
    def convert_st(self):
        """ handle the conversion from SimpleGUI to Tkinter, and save the result """
        
        # check first if a file was selected and that it contains any data
        if not self.input_data:
            nofile_text = "Please, choose a file to convert with data in it."
            tkMessageBox.showinfo("No file selected!", message=nofile_text)
            return
        
        # conversion of the input file by calling the Simplegui2Tkinter class
        output_data = Simplegui2Tkinter(self.input_data).convert()
        
        # return an error message if the input file has no SimpleGUI module
        if "___NoSimpleguiFound!___" in output_data:
            error_text = "Wrong file? No SimpleGUI module was found in this file..."
            tkMessageBox.showinfo("Done!", message=error_text)
            return
        
        # save the output file
        output_file = open(self.entry_save.get(), "w")
        output_file.write(output_data)
        output_file.close()
        
        # signal user the work is done and clear "entry_open" and "entry_save"
        finished_text = "SUCCESS! Conversion from SimpleGUI to Tkinter finished!"
        tkMessageBox.showinfo("Done!", message=finished_text)
        
        self.entry_open.delete(0, Tkinter.END)
        self.entry_save.delete(0, Tkinter.END)



# create the application window
window_root = Tkinter.Tk()
window_root.title("SimpleGUI/Tkinter converter")

app = Window_App(window_root)

# initiate the application window
window_root.mainloop()
