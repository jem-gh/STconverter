###########################################################################
# 
# Here is an example of images processed and displayed on canvas. These 
# images are in purpose not really pretty to limit people claiming them as 
# his/her own. ;-)
# 
###########################################################################


# DIFFICULTIES
# 
# - several images file formats: PNG, JPG, GIF
# - process and display several time the same image or parts/tiles of this image


import simplegui


### global variables and handler

angle = 0

def timer_handler():
    global angle
    angle += 1

angle2 = 0

def timer2_handler():
    global angle2
    angle2 += 1


# initial coordinates and update function of the image which can be dragged
coor = [350, 450]

def pos_update(pos):
    coor[0], coor[1] = pos[0], pos[1]


### download images
# JPG: direct link
image_jpg = simplegui.load_image("https://dl.dropbox.com/u/107991322/STconverter/jpg.jpg")
# GIF: from variable
link_gif = "https://dl.dropbox.com/u/107991322/STconverter/gif.gif"
image_gif = simplegui.load_image(link_gif)
# PNG: from list
stuffs = [23, "notme", "https://dl.dropbox.com/u/107991322/STconverter/png.png", "end"]
image_png = simplegui.load_image(stuffs[2])
# main image, with comment
link_image = "https://dl.dropbox.com/u/107991322/STconverter/main.png"
image = simplegui.load_image(link_image) # "the" comment !!!

image_drag = simplegui.load_image("https://dl.dropbox.com/u/107991322/STconverter/drag.png")


### drawing handler
def draw(c):
    
    c.draw_image(image, (250,250), (500,500), (250,250), (500,500)) # WITH COMMENT!!!
    
    c.draw_image(image, (165,350), (230,230), (150,600), (75,75), 20)
    c.draw_image(image, (165,350), (230,230), (75,550), (35,35), angle)
    c.draw_image(image, (165,350), (230,230), (325,650), (50,50), -angle2)
    c.draw_image(image, (335,150), (240,240), (270,670), (35,35), -angle)
    c.draw_image(image, (335,150), (240,240), (450,540), (50,50), angle2)
    
    c.draw_image(image_jpg, (50,50), (100,100), (75,650), (75,75))
    c.draw_image(image_gif, (50,50), (100,100), (275,575), (75,75))
    c.draw_image(image_png, (50,50), (100,100), (400,615), (75,75))
    
    c.draw_image(image_drag, (38,20), (76,41), coor, (76,41))


### create frame and canvas
frame = simplegui.create_frame('An Example with images!', 500, 700, 0)
frame.set_draw_handler(draw)
frame.set_canvas_background('White')


timer = simplegui.create_timer(1000, timer_handler)
timer.start()

timer2 = simplegui.create_timer(100, timer2_handler)
timer2.start()


frame.set_mousedrag_handler(pos_update)


### start frame
frame.start()
