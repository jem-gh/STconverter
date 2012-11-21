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
import urllib2      # used by up_music()
import random       # used by up_image()



# global variables
input_data = ""
input_name = ""
output_data = ""



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
"Pc": "(\w+|[\[\(\w\+\-\*\/\%\. ]+,?[\w\+\-\*\/\%\. \]\)]*)", 
    # PARAMETER MULTILINE: digit, variable, list, operation, tuple, multiline
"Pm" : "(\w+[\[\w\]]+|[\w\+\-\*\/\%\.\[\(\]\)\s,\\\\]+)", 
    # PARAMETER QUOTED: variable, list, quoted string
"Pq" : "([\"\'].+?[\"\']|\w+[\[\(\w\]\)]+)", 
    # SPACE: comma, space, \n, \
"S"  : "(?: *,[\s\\\]*)", 
    # COMMENT
"M"  : "( *#?.*)"
}



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
        self.up_image()
        self.up_key()
        self.up_mouse()
        self.up_ini()
        self.up_Tkinter_incompatible()
    
    
    def up_module(self):
        """ update simplegui module to Tkinter and add division from future """
        
        global output_data
        
        # update simplegui module to Tkinter
        MODULE_RE = re.compile(r'^(import [\w ,]*)simplegui', re.MULTILINE)
        output_data = MODULE_RE.sub(r'\1Tkinter', input_data)
        
        # add division from future to enable true division in Python 2.7
        output_data = re.sub("^((?:\s|(?:#.*\n))*)", 
                             "\\1\n\nfrom __future__ import division\n\n", 
                             output_data)
    
    
    def up_frame_canvas(self):
        """ update the Frame and Canvas widget """
        
        global output_data
        
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
        if "set_draw_handler" not in output_data:
            output_data = FRAME_RE.sub(tk_frame, output_data)
            return
        
        
        # update drawing handler
        sg_drawing_handler = "{I}def {n}\( *{N} *\):\n"
        tk_drawing_handler = "\\1def {n}(\\2):\n" \
                             "\\1    \\2.delete('all')\n" \
                             "\\1    \n"
        
        draw_n = re.findall('\w+.set_draw_handler\( *{N} *\)'.format(N=RNI["N"]), 
                            output_data)[0]
        output_data = re.sub(sg_drawing_handler.format(I=RNI["I"], n=draw_n, 
                                 N=RNI["N"]), 
                             tk_drawing_handler.format(n=draw_n), 
                             output_data)
        
        # create canvas with size used in "simplegui.create_frame"
        # and with a black background by default
        bg = ("'Black'", "")
        if ".set_canvas_background" in output_data:
            bg = re.findall(sg_bg, output_data)[0]
            output_data = re.sub(sg_bg, '', output_data)
        output_data = FRAME_RE.sub(r'{f}\n{c}{b}'.format(f=tk_frame, c=tk_canvas, 
                                    b=tk_bg.format(b=bg[0], m=bg[1])), 
                                   output_data)
        
        # replace "set_draw_handler" with drawing handler call
        refresh_time = 17 # in ms (66ms~15fps; 33ms~30fps; 17ms~60fps)
        
        dh_old = "{I}\w+.set_draw_handler\( *{h} *\){M}".format(
                     I=RNI["I"], h=draw_n, M=RNI["M"])
        dh_new = "\\1def refresh_canvas():\\2\n" \
                 "\\1    {h}(canvas)\n" \
                 "\\1    window_root.after({t}, refresh_canvas)\n\n" \
                 "\\1refresh_canvas()\n".format(h=draw_n, t=refresh_time)
        output_data = re.sub(dh_old, dh_new, output_data)
        
        
        # update Canvas methods
        # Text
        sg_txt = "{C}.draw_text\( *{Pq}{S}{Pc}{S}{P}{S}{Pq} *\)".\
                 format(C=RNI["C"], Pq=RNI["Pq"], S=RNI["S"], 
                        Pc=RNI["Pc"], P=RNI["P"])
        tk_txt = "\\1.create_text(\\3, anchor='sw', " \
                 "text=\\2, font=('DejaVu Serif Condensed', \\4), fill=\\5)"
        output_data = re.sub(sg_txt, tk_txt, output_data)
        
        # Oval
        sg_circle = "{C}.draw_circle\( *{Pm}{S}{P}{S}{P}{S}{Pq}{S}?{Pq}? *\)".\
                    format(C=RNI["C"], Pm=RNI["Pm"], S=RNI["S"], P=RNI["P"], 
                           Pq=RNI["Pq"])
        tk_oval =     '{c}.create_oval(({x1},{y1},{x2},{y2}), width={w}, ' \
                      'outline={l}, fill={f})'
        tk_oval_var = 't_x, t_y = {v}\n' \
                      '{s}t_r = {r}\n' \
                      '{s}t_x1, t_x2 = (t_x - t_r), (t_x + t_r)\n' \
                      '{s}t_y1, t_y2 = (t_y - t_r), (t_y + t_r)\n' \
                      '{s}{n}{c}.create_oval((t_x1,t_y1,t_x2,t_y2), width={w}, ' \
                      'outline={l}, fill={f})'
        
        ovals = re.findall(sg_circle, output_data)
        
        for oval in ovals:
            
            # if coord and rad use digit only, without variables nor operations
            is_pos_digit = not re.findall(r"[a-zA-Z\+\-\*\/\%]", oval[1])
            is_rad_digit = not re.findall(r"[a-zA-Z\+\-\*\/\%]", oval[2])
            if is_pos_digit and is_rad_digit:
                c, xy, r, w, l, f = oval
                x, y = re.findall(r"\d+", xy)
                x1, x2 = (int(x) - int(r)), (int(x) + int(r))
                y1, y2 = (int(y) - int(r)), (int(y) + int(r))
                fill = f if f else '""'
                output_data = re.sub("{c}.draw_circle\( *" \
                                     "{xy}{S}{r}{S}{w}{S}{l}{S}?{f} *\)".\
                                     format(c=c, xy=re.escape(xy), S=RNI["S"], 
                                            r=r, w=re.escape(w), l=re.escape(l), 
                                            f=re.escape(f)), 
                                     tk_oval.format(c=c, x1=x1, y1=y1, x2=x2, 
                                                    y2=y2, w=w, l=l, f=fill), 
                                     output_data)
            
            # if position and/or radius is a variable
            else:
                c, var, r, w, l, f = oval
                name = re.findall(r"(\w+ *= *)?{c}.draw_circle\( *" \
                                   "{v}{S}{r}{S}{w}{S}{l}{S}?{f} *\)".\
                                   format(c=c, v=re.escape(var), S=RNI["S"], 
                                          r=re.escape(r), w=re.escape(w), 
                                          l=re.escape(l), f=re.escape(f)), 
                                  output_data)
                name = name[0] if name else ''
                space = re.findall(r"( *){n}{c}.draw_circle\( *" \
                                    "{v}{S}{r}{S}{w}{S}{l}{S}?{f} *\)".\
                                    format(n=name, c=c, v=re.escape(var), 
                                           S=RNI["S"], r=re.escape(r), 
                                           w=re.escape(w), l=re.escape(l), 
                                           f=re.escape(f)), 
                                   output_data)
                space = space[0] if space else ''
                fill = f if f else '""'
                output_data = re.sub(r"{n}{c}.draw_circle\( *" \
                                      "{v}{S}{r}{S}{w}{S}{l}{S}?{f} *\)".\
                                      format(n=name, c=c, v=re.escape(var), 
                                             S=RNI["S"], r=re.escape(r), 
                                             w=re.escape(w), l=re.escape(l), 
                                             f=re.escape(f)), 
                                     tk_oval_var.format(v=var, s=space, n=name, 
                                             c=c, r=r, w=w, l=l, f=fill), 
                                     output_data)
        
        # Line
        sg_line = "{C}.draw_line\( *{Pc}{S}{Pc}{S}{P}{S}{Pq} *\)".\
                  format(C=RNI["C"], Pc=RNI["Pc"], S=RNI["S"], 
                         P=RNI["P"], Pq=RNI["Pq"])
        tk_line = "\\1.create_line(\\2, \\3, width=\\4, fill=\\5)"
        output_data = re.sub(sg_line, tk_line, output_data)
        
        # Polyline
        sg_pline = "{C}.draw_polyline\( *{Pm}{S}{P}{S}{Pq} *\)".\
                   format(C=RNI["C"], Pm=RNI["Pm"], S=RNI["S"], 
                          P=RNI["P"], Pq=RNI["Pq"])
        tk_pline = "\\1.create_line(\\2, width=\\3, fill=\\4)"
        output_data = re.sub(sg_pline, tk_pline, output_data)
        
        # Polygon
        sg_poly = "{C}.draw_polygon\( *{Pm}{S}{P}{S}{Pq}{S}?{Pq}? *\)".\
                  format(C=RNI["C"], Pm=RNI["Pm"], S=RNI["S"], 
                         P=RNI["P"], Pq=RNI["Pq"])
        tk_poly = "{n}.create_polygon({c}, width={w}, outline={o}, fill={f})"
        polygons = re.findall(sg_poly, output_data)
        for p in polygons:
            fill = p[4] if p[4] else '""'
            output_data = re.sub('{n}.draw_polygon\( *{a}{S}{w}{S}{c}{S}?{f} *\)'.\
                                 format(n=p[0], a=re.escape(p[1]), S=RNI["S"], 
                                        w=re.escape(p[2]), c=re.escape(p[3]), 
                                        f=re.escape(p[4])), 
                                 tk_poly.format(n=p[0], c=p[1], w=p[2], o=p[3], 
                                        f=fill), 
                                 output_data)
    
    
    def up_button(self):
        """ update Button widget(s) """
        
        global output_data
        
        sg_button = "{C}.add_button\( *{Pq}{S}{N}{S}?{P}? *\){M}".\
                    format(C=RNI["C"], Pq=RNI["Pq"], S=RNI["S"], N=RNI["N"], 
                           P=RNI["P"], M=RNI["M"])
        sg_b_ch =   "{I}(?:\w+ *= *)?{f}.add_button\( *{m}{S}{h}{S}?{s} *\){M}"
        tk_b_ws = "\\1{h}_bt = Tkinter.Button({f}, text={m}, command={h})\\2\n" \
                  "\\1{h}_bt.config(width={s})\n" \
                  "\\1{h}_bt.pack()\n"
        tk_b_ns = "\\1{h}_bt = Tkinter.Button({f}, text={m}, command={h})\\2\n" \
                  "\\1{h}_bt.pack()\n"
        
        buttons = re.findall(sg_button, output_data)
        
        for button in buttons:
            # decrease by a factor 10 the button size (if any) to fit Tkinter 
            size = button[3] if button[3] else ''
            is_size_digit = not re.findall(r"[a-zA-Z\+\-\*\/\%]", size)
            if size and is_size_digit:
                size = int(size) / 10
            
            if size:
                output_data = re.sub(sg_b_ch.format(I=RNI["I"], f=button[0], 
                                         m=re.escape(button[1]), S=RNI["S"], 
                                         h=button[2], s=re.escape(button[3]), 
                                         M=RNI["M"]),
                                     tk_b_ws.format(f=button[0], m=button[1], 
                                         h=button[2], s=size), 
                                     output_data)
            elif not size:
                output_data = re.sub(sg_b_ch.format(I=RNI["I"], f=button[0], 
                                         m=re.escape(button[1]), S=RNI["S"], 
                                         h=button[2], s=re.escape(button[3]), 
                                         M=RNI["M"]),
                                     tk_b_ns.format(f=button[0], m=button[1], 
                                         h=button[2]), 
                                     output_data)
    
    
    def up_label(self):
        """ update Label widget(s) """
        
        global output_data
        
        sg_label =    "{No} *=? *{C}.add_label\( *{Pq}{S}?{P}? *\)".\
                      format(No=RNI["No"], C=RNI["C"], Pq=RNI["Pq"], 
                             S=RNI["S"], P=RNI["P"])
        sg_label_nv  = "{I}{n} *=? *{f}.add_label\( *{m}{S}?{s} *\)"
        sg_label_wv  = "{I}{n} *= *{f}.add_label\( *{m}{S}?{s} *\)"
        tk_label_nv = "\\1Tkinter.Label({f}, text={m}).pack()"
        tk_label_wv = "\\1{n}_var = Tkinter.StringVar()\n" \
                      "\\1{n} = Tkinter.Label({f}, textvariable={n}_var).pack()\n" \
                      "\\1{n}_var.set({m})"
        
        # find all labels in order to differentiate the ones using text variable
        labels = re.findall(sg_label, output_data)
        
        for l in labels:
            # not using text variable
            if ("\n{n}.set_text".format(n=l[0]) and 
                " {n}.set_text".format(n=l[0])) not in output_data:
                output_data = re.sub(sg_label_nv.format(I=RNI["I"], n=l[0], 
                                         f=l[1], S=RNI["S"], m=re.escape(l[2]), 
                                         s=re.escape(l[3])), 
                                     tk_label_nv.format(f=l[1], m=l[2]), 
                                     output_data)
            
            # using text variable
            else:
                # update setting message
                output_data = re.sub(r"([\n ]){n}.set_text\(".format(n=l[0]), 
                                     r"\1{n}_var.set(".format(n=l[0]), 
                                     output_data)
                # update Label
                output_data = re.sub(sg_label_wv.format(I=RNI["I"], n=l[0], 
                                         f=l[1], S=RNI["S"], m=re.escape(l[2]), 
                                         s=re.escape(l[3])), 
                                     tk_label_wv.format(n=l[0], f=l[1], m=l[2]), 
                                     output_data)
    
    
    def up_input(self):
        """ update Entry/Input widget(s) """
        
        global output_data
        
        if "add_input" in output_data:
            
            sg_input = "{I}{No} *=? *{C}.add_input\( *{Pq}{S}{N}{S}{P} *\){M}"
            tk_input = "{i}{n}_lb = Tkinter.Label({f}, text={l})\\1\n" \
                       "{i}{n}_lb.pack()\n" \
                       "{i}{n}_et = Tkinter.Entry({f})\n" \
                       "{i}{n}_et.bind('<Return>', {n})\n" \
                       "{i}{n}_et.config(width={s})\n" \
                       "{i}{n}_et.pack()\n"
            sg_inp_fn_p = "def {n}\( *{N} *\):"
            sg_inp_fn   = "def {n}\( *{p} *\): *(?:\n .*)+[=( \-+*/]{p}[) \-+*/\n]"
            param_def   = "(?<=(?<!{i})[= \(\-+*/]){p}(?=[ \)\-+*/\n])"

            inputs = re.findall(sg_input.format(I=RNI["I"], No=RNI["No"], 
                                    C=RNI["C"], Pq=RNI["Pq"], S=RNI["S"], 
                                    N=RNI["N"], P=RNI["P"], M=RNI["M"]), 
                                output_data)
            
            for i in inputs:
                # retrieve parameter name used in the Input handler
                param = re.findall(sg_inp_fn_p.format(n=i[4], N=RNI["N"]), 
                                   output_data)[0]
                
                # find and update parameter in the Input handler
                handler_old = re.findall(sg_inp_fn.format(n=i[4], p=param), 
                                         output_data)[0]
                handler_new = re.sub(param_def.format(i=i[4], p=param), 
                                     "{}_et.get()".format(i[4]), 
                                     handler_old)
                output_data = output_data.replace(handler_old, handler_new)
                
                ## write Tkinter GUI of the Input widget
                tk_input_size = "int(" + i[5] + "/10)"
                output_data = re.sub(sg_input.format(I=i[0], No=i[1], C=i[2], 
                                         Pq=re.escape(i[3]), S=RNI["S"], N=i[4], 
                                         P=re.escape(i[5]), M=RNI["M"]), 
                                     tk_input.format(i=i[0], n=i[4], f=i[2], 
                                         l=i[3], s=tk_input_size), 
                                     output_data)
    
    
    def up_timer(self):
        """ update timer event """
        
        global output_data
        
        if ".create_timer(" in output_data:
            
            # retrieve all Timer widgets' names
            timer_names = re.findall("{N} *= *simplegui.create_timer\(".format(
                                         N=RNI["N"]), 
                                     output_data)
            
            for t in timer_names:
                # update timer event handler
                sg_timer_start = "{}\.start\(\)".format(t)
                sg_timer_stop =  "{}\.stop\(\)".format(t)
                tk_timer_start = "{}_st(True)".format(t)
                tk_timer_stop =  "{}_st(False)".format(t)
                output_data = re.sub(sg_timer_start, tk_timer_start, output_data)
                output_data = re.sub(sg_timer_stop, tk_timer_stop, output_data)
                
                # update timer
                sg_timer = "{I}{t} *= *simplegui.create_timer"\
                           "\( *{P}{S}{N} *\){M}"
                tk_timer = "\\1{t}_status = False\n\n" \
                           "\\1def {t}_st(status):\n" \
                           "\\1    global {t}_status\n" \
                           "\\1    {t}_status = status\n\n" \
                           "\\1def {t}_fn():\\4\n" \
                           "\\1    window_root.after(\\2, {t}_fn)\n" \
                           "\\1    if {t}_status:\n" \
                           "\\1        \\3()\n\n" \
                           "\\1{t}_fn()\n"
                output_data = re.sub(sg_timer.format(I=RNI["I"], t=t, P=RNI["P"], 
                                         S=RNI["S"], N=RNI["N"], M=RNI["M"]), 
                                     tk_timer.format(t=t), 
                                     output_data)
    
    
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
            m_all = re.findall("{No} *=? *simplegui.load_sound\( *{Pq} *\)".\
                                   format(No=RNI["No"], Pq=RNI["Pq"]), 
                               output_data)
            
            # verify or find source path of each music/sound
            for m in range(len(m_all)):
                if m_all[m][1][0] not in ["'", '"']:
                    # if the link is in a list
                    if "[" in m_all[m][1]:
                        ref = re.findall("\w+", m_all[m][1])
                        l = re.findall("{l} *= *\[\s*{Pq}+\s*\]".format(
                                           l=ref[0], Pq=RNI["Pq"], S=RNI["S"]), 
                                       output_data, re.S)
                        l = re.split(" *, *\n? *", l[0])[int(ref[1])][1:-1]
                        m_all[m] = [m_all[m], l]
                    
                    # if the link is the value of a variable
                    elif "[" not in m_all[m][1]:
                        m_all[m] = [m_all[m], re.findall("{m} *= *{Pq}".format(
                                        m=m_all[m][1], Pq=RNI["Pq"]), 
                                    output_data)[0][1:-1]]
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
                output_data = re.sub(sg_load, tk_load, output_data)
                sg_play = "{n}.play\(\)".format(n=m[0])
                tk_play = "pygame.mixer.music.play(-1, pygame.mixer.music.get_pos())"
                output_data = re.sub(sg_play, tk_play, output_data)
                sg_pause = "{n}.pause\(\)".format(n=m[0])
                tk_pause = "pygame.mixer.music.pause()"
                output_data = re.sub(sg_pause, tk_pause, output_data)
                sg_rewind = "{n}.rewind\(\)".format(n=m[0])
                tk_rewind = "pygame.mixer.music.rewind()"
                output_data = re.sub(sg_rewind, tk_rewind, output_data)
                sg_vol = "{n}.set_volume\((.*)\)".format(n=m[0])
                tk_vol = "pygame.mixer.music.set_volume(\\1)"
                output_data = re.sub(sg_vol, tk_vol, output_data)
            
            
            # update others musics/sounds to use the pygame sound module
            output_data = re.sub("simplegui.load_sound\((.*)\)",
                                 "pygame.mixer.Sound(urllib.urlretrieve(\\1)[0])",
                                 output_data)
    
    
    def up_image(self):
        """ update images using the Python Imaging Library (PIL) with ImageTk """
        
        global output_data
        
        if ".draw_image" in output_data:
            
            # add Python Imaging Library (PIL) (to process images) and urllib 
            # (to retrieve images from Internet) if not yet available
            
            m_tk =  "(import +.*Tkinter.*\n)"
            m_url = "(import +.*urllib.*\n)"
            n_url = "\\1import urllib\n" \
                    "from PIL import Image, ImageTk\n"
            w_url = "\\1from PIL import Image, ImageTk\n"
            
            # function which will process all images in the converted file, and 
            # return images Tkinter-compatible, with:
            # img = source image retrieved from Internet 
            # src_coor, src_size = coordinates (x, y) and size (width, height) 
            #                      in pixels of a selection of the source image 
            # dest_size = size (width, height) in pixels on the canvas of the 
            #             selected part of the image 
            # a = angle in radians of clockwise rotation around its center 
            fn = "\ndef STconverter_image(img, src_coor, src_size, dest_size, a):\n" \
                 "    x1, y1 = (src_coor[0]-src_size[0]/2), (src_coor[1]-src_size[1]/2)\n" \
                 "    x2, y2 = (src_coor[0]+src_size[0]/2), (src_coor[1]+src_size[1]/2)\n" \
                 "    image_croped = img.crop((int(x1), int(y1), int(x2), int(y2)))\n" \
                 "    image_resized = image_croped.resize(dest_size)\n" \
                 "    image_rotated = image_resized.rotate(-a)\n" \
                 "    return ImageTk.PhotoImage(image_rotated)\n\n"
            
            if "urllib" in output_data:
                output_data = re.sub(m_url, w_url+fn, output_data)
            else:
                output_data = re.sub(m_tk, n_url+fn, output_data)
            
            
            # update all images loading
            output_data = re.sub("{I}{N} *=? *simplegui.load_image\( *{Pq} *\)".\
                                 format(I=RNI["I"], N=RNI["N"], Pq=RNI["Pq"]), 
                                 "\\1\\2 = Image.open(urllib.urlretrieve(\\3)[0])\n" \
                                 "\\1\\2_displayed = ''\n", 
                                 output_data)
            
            
            # update all images drawing
            sg_image = "{I}{N}.draw_image" \
                       "\( *{N}{S}{Pc}{S}{Pc}{S}{Pc}{S}{Pc}{S}?{P}? *\){M}"
            sg_img_c = "{i}{c}.draw_image" \
                       "\( *{n}{S}{sc}{S}{ss}{S}{dc}{S}{ds}{S}?{a}? *\){M}"
            tk_image = "{i}global {n}_displayed\n" \
                       "{i}{n}_params = ({im}, {sc}, {ss}, {ds}, {a})\n" \
                       "{i}{n}_displayed = STconverter_image(*{n}_params)\n" \
                       "{i}{c}.create_image({dc}, image={n}_displayed)\\1\n"
            
            images = re.findall(sg_image.format(I=RNI["I"], N=RNI["N"], S=RNI["S"], 
                                    Pc=RNI["Pc"], P=RNI["P"], M=RNI["M"]), 
                                output_data)
            
            used_once = []
            
            for i in images:
                # check angle
                angle = i[7] if i[7] else 0
                
                # check if the image name is already used (when the same image 
                # is used for several displays)
                if i[2] not in used_once:
                    used_once.append(i[2])
                    name = i[2]
                else:
                    # give a new name
                    extension = ''.join(random.sample("abcdefghij0123456789", 6))
                    name = i[2] + extension
                    # add a global variable
                    output_data = re.sub("{I}({im}_displayed = ''\n)".format(
                                             I=RNI["I"], im=i[2]), 
                                         "\\1\\2" \
                                         "\\1{n}_displayed = ''\n".format(n=name),
                                         output_data)
                
                output_data = re.sub(sg_img_c.format(i=i[0], c=i[1], n=i[2], 
                                         sc=re.escape(i[3]), ss=re.escape(i[4]), 
                                         dc=re.escape(i[5]), ds=re.escape(i[6]), 
                                         a=re.escape(i[7]), S=RNI["S"], M=RNI["M"]), 
                                     tk_image.format(i=i[0], n=name, im=i[2], 
                                         sc=i[3], ss=i[4], c=i[1], dc=i[5], 
                                         ds=i[6], a=angle), 
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
                                 "canvas.bind('<Button-1>', \\1)\n",
                                 output_data)
    
    
    def up_ini(self):
        """ update the initialization of the window event loop """
        
        global output_data
        
        # if no frame, return
        if "Tkinter.Frame" not in output_data:
            return
        
        frame = re.findall(r"{N} = Tkinter.Frame\(".format(N=RNI["N"]), 
                           output_data)[0]
        output_data = re.sub("{f}.start\(\){M}".format(f=frame, M=RNI["M"]), 
                             "", 
                             output_data)
        output_data = output_data + "\n\nwindow_root.mainloop()\n"
    
    
    def up_Tkinter_incompatible(self):
        
        global output_data
        
        """ some color names specified to draw object in SimpleGUI canvas 
            aren't always well recognized by Tkinter ... change to their 
            RGB value """
        output_data = re.sub(r"[\"\']Aqua[\"\']", r"'#00FFFF'", output_data)
        output_data = re.sub(r"[\"\']Fuchsia[\"\']", r"'#FF00FF'", output_data)
        output_data = re.sub(r"[\"\']Lime[\"\']", r"'#00FF00'", output_data)
        output_data = re.sub(r"[\"\']Olive[\"\']", r"'#808000'", output_data)
        output_data = re.sub(r"[\"\']Silver[\"\']", r"'#C0C0C0'", output_data)
        output_data = re.sub(r"[\"\']Teal[\"\']", r"'#008080'", output_data)
        
        """ SimpleGUI handles doc strings ending with four double quotes 
            which is not always well handled by other Python interpreters """
        output_data = re.sub('""""', '"""', output_data)




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
