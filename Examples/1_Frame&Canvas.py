###########################################################################
# 
# Here is an example of code working in CodeSkulptor with SimpleGUI
# (code not very useful to say the truth... and NOT AT ALL pretty) 
# just to show different types of widgets (Entry, Button, Label...) and
# canvas objects (Text, Line, Circle...)
# Look at the result after conversion to Tkinter!
# 
###########################################################################


# DIFFICULTIES
# 
# - expression on Python can be written in really a lot of different ways 
#   (spaces or not, with digits or variables/lists...)


import simplegui
import random # for "text_slide_ch", "text_move_ch"



### global variable(s)
control_width = 200
canvas_width = 400
canvas_height = 600

# message of the texts on canvas with single or double quotes
txt_slide_mes = "Sliding!!! =)" 
txt_move_mes = 'Moving around!!! =)'
# position of the text on canvas with parentheses or square brackets
txt_slide_pos = [0, 40] 
txt_move_pos = (150, 250)
txt_size = 18
txt_move_color = "Red" # predefined color of the text moving around randomly

another_test_mes = "" # message... from another test

# variable with digits or calculations
circle_pos = [ canvas_width / 4, canvas_height / 7 * 5 ]
circle_rad = 10
circle_w = 5
# variable with single or double quotes
circle_color = "Purple"
circle_fill = 'Cyan'

line_start = [canvas_width / 4, canvas_height / 7 * 5]
line_end = [150, 375]
line_w = 3
line_color = "Purple"

plinecoord = [(253, 545), (287, 599), (302, 532), (336, 588)]
plinesize = 3
plinecolor = "Fuchsia"

polygon_pos = [((canvas_width - 100) / 2,355),(190,355),(190,395),(150,395)]
polygon_w = 5
polygon_color = "Purple"
polygon_fill = 'Cyan'

timer_interval = 1500

button_label = "Stop"
input_label = 'Try to enter some text here:'



### helper function(s)
def output_format(text):
    alph = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    num = "0123456789"
    
    char = len(list(x for x in text if x in alph))
    digit = len(list(x for x in text if x in num))
    others = len(text) - char - digit
    return "Your text has " + str(char) + " letter(s), " + \
           str(digit) + " digit(s), " + str(others) + " other characters or spaces."



### event handler(s)
def text_slide_ch():
    if txt_slide_pos[0] == canvas_width:
        txt_slide_pos[0] = 0
    else:
        txt_slide_pos[0] += 2

def text_move_ch():
    global txt_move_pos
    x = random.randrange(0, canvas_width)
    y = random.randrange(0, canvas_height)
    txt_move_pos = (x, y)

def txt_slide_update(text):
    global txt_slide_mes
    txt_slide_mes = text

def txt_move_update(text):
    global txt_move_mes
    txt_move_mes = text

def change_color():
    global txt_move_color
    color = random.choice(["Black", "Cyan", "Blue", "Green", "Red", "Orange", "Grey", "Yellow"])
    if color == txt_move_color:
        change_color()
    else:
        txt_move_color = color

def timers_start():
    timer_txt_slide.start()
    timer_txt_move.start()

def timers_stop():
    timer_txt_slide.stop()
    timer_txt_move.stop()

def another_test(t):
    global another_test_mes
    another_test_mes = output_format(t)
    another_label.set_text(another_test_mes)



### drawing handler
def draw(c):
    ### line ###
    # with parentheses and double quotes
    c.draw_line((50, 100), (350, 400), 5, "Blue")
    # with square brackets, name, and single quotes
    line = c.draw_line([350, 100], [50, 400], 2, 'Red')
    
    ### polyline ###
    # with parentheses and double quotes
    c.draw_polyline([(253, 525), (287, 579), (302, 512), (336, 567)], 4, "Blue")
    # with square brackets, name, and single quotes
    pline = c.draw_polyline([[253, 530], [287, 584], [302, 517], [336, 572]], 4, 'Red')
    
    ### polygon with or without background ###
    # with parentheses, and single quotes
    c.draw_polygon([(50, 200), (100, 200), (100, 250)], 3, 'Green', 'White') 
    # with square brackets, name, and double quotes
    pol = c.draw_polygon([[50, 250], [100, 250], [100, 300]], 6, "Pink")
    
    ### circle with or without background ###
    # with parentheses, and double quotes
    c.draw_circle((250, 250), 20, 3, "Blue", "Orange") 
    # with square brackets, name, and single quotes
    cir = c.draw_circle([250, 250], 100, 10, 'Green') 
    
    ### text on canvas with predefined options or variables ###
    # with parentheses, and double quotes
    c.draw_text("I don't move... =(", (230, 430), 12, "Grey") 
    # with name, square brackets, and single quotes
    txxxt = c.draw_text('test of drawing on canvas', [260, 490], 8, 'Black') 
    
    ### code written with a baseball bat!!! ###
    c.draw_line([23  ,478  ]  ,(  212  ,437)  ,7  ,"Black")
    c.draw_polygon( [ (89,498)  ,  [  36  ,437],(178,   490) ],6,'Pink'  ,"Green")
    c.draw_circle(      (  123   ,   467),20  ,     3,  "Blue",'Orange'   )
    c.draw_polyline(   [  (  253 , 535 )  , ( 287  , 589 ) , ( 302  , 522 ) , (336, 578  ) ] , 4  , "Green"  )
    
    ### text, line, polygon, circle on several lines ###
    c.draw_text("Me, I'm here!!!", \
                (27, 587), \
                10, \
                "Yellow") 
    c.draw_line((175, 83), \
                (233, 113), \
                5, \
                "Fuchsia")
    c.draw_polyline([(253, 540), (287, 594), \
                     (302, 527), (336, 583)], \
                     4, \
                     "Yellow")
    c.draw_circle((200, 95), \
                  10, \
                  3, \
                  "Maroon", 
                  "Silver")
    c.draw_polygon([(203, 93), (223, 80), (243, 98), \
                    (233, 116), (213, 110)], \
                    2, \
                    'Teal', \
                    'Olive') 
    
    
    ### text, line, polygon, circle using variables ###
    c.draw_line(line_start, line_end, line_w, line_color)
    c.draw_polyline(plinecoord, plinesize, plinecolor)
    c.draw_polygon(polygon_pos, polygon_w, polygon_color, polygon_fill)
    c.draw_circle(circle_pos, circle_rad, circle_w, circle_color, circle_fill)
    c.draw_text(txt_slide_mes, txt_slide_pos, 24, 'Green') 
    c.draw_text(txt_move_mes, txt_move_pos, txt_size, txt_move_color)
    



### create frame and canvas
frame = simplegui.create_frame('An Example!', \
                               canvas_width, \
                               canvas_height, \
                               control_width)
frame.set_draw_handler(draw)
frame.set_canvas_background('#333366')



### register event handlers
# Timers
timer_txt_slide = simplegui.create_timer(100, text_slide_ch)
# with variable for interval and on several lines
timer_txt_move = simplegui.create_timer(timer_interval, \
                                        text_move_ch) 

# Input/Entry fields with labels
# with double quotes
frame.add_input("Change text of sliding message:", txt_slide_update, 150) 
# with single quotes, and name
inp = frame.add_input('Change text of moving message:', txt_move_update, 150) 

# Buttons and Labels
# with double quotes, and name
label = frame.add_label("Change color of the moving text") 
button = frame.add_button("Change", change_color, 100) 
# with single quotes
frame.add_label('Start/Stop the text moving') 
frame.add_button('Start', timers_start, 100) 

# Button, Input, Label with variables and on several lines
frame.add_button(button_label, \
                 timers_stop, \
                 100)
frame.add_input(input_label, \
                another_test, \
                150)
another_label = frame.add_label(another_test_mes)



### start frame and timers
frame.start()
timer_txt_slide.start()
timer_txt_move.start()
