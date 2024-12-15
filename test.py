from pyray import *

APP_WIDTH =800
APP_HEIGHT =450

init_window(APP_WIDTH, APP_HEIGHT, "Calculator")

rec = Rectangle(100, 100, 200, 200)

flipping = False
expanding = False

while not window_should_close():
    
    if is_key_pressed(KeyboardKey.KEY_SPACE) and not flipping and not expanding:
        
            flipping = True

    if flipping:
          
        rec.width -= 1500 * get_frame_time()
        rec.x += 750 * get_frame_time()

    if rec.width <= 0:
        
        flipping = False
        expanding = True

    if expanding:
         
        rec.width += 1500 * get_frame_time()
        rec.x -= 750 * get_frame_time()

    if rec.width >= 200:
        
        expanding = False

    begin_drawing()
    clear_background(RAYWHITE)
    draw_rectangle_rec(rec, MAROON)
    end_drawing()

close_window()