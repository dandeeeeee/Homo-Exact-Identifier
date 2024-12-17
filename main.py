import os
from pyray import *
from raylib import ffi

from font_hex import font_hex
from font_hex_italic import font_hex_italic


vertex_shader_code = """
#version 330

in vec3 vertexPosition;
in vec2 vertexTexCoord;

uniform mat4 mvp;

out vec2 fragTexCoord;

void main() {
    fragTexCoord = vertexTexCoord;
    gl_Position = mvp * vec4(vertexPosition, 1.0);
}
"""


fragment_shader_code = """
#version 330

const float PI = 3.14159265359;

uniform vec2 resolution;
uniform float iTime;

float message(vec2 uv) {
    uv -= vec2(1.0, 10.0);
    if (uv.x < 0.0 || uv.x >= 32.0 || uv.y < 0.0 || uv.y >= 3.0) return -1.0;
    int i = 1, bit = int(pow(2.0, floor(32.0 - uv.x)));
    if (int(uv.y) == 2) i = 928473456 / bit;  // 00110111 01010111 01100001 01110000
    if (int(uv.y) == 1) i = 626348112 / bit;  // 00100101 01010101 01010000 01010000
    if (int(uv.y) == 0) i = 1735745872 / bit; // 01100111 01110101 01100001 01010000
    return float(i - 2.0 * (i / 2));
}

void main() {
    vec2 uv = gl_FragCoord.xy / resolution;
    float c = message(uv);
    if (c >= 0.0) {
        gl_FragColor = vec4(c, c, c, 1.0);  // Apply grayscale color
        return;
    }

    gl_FragColor = vec4(uv, 0.5 + 0.5 * sin(iTime), 1.0);
}
"""



APP_WIDTH = 750
APP_HEIGHT = 1200  

MATTE_BLACK = Color(51, 51, 51, 255)
GOLDEN_YELLOW = Color(255, 223, 0, 255)


HOVERED_REC_EXPAND_SPEED = 700


class Button:

    def __init__(self, pos: Vector2, text: str, font: Font, font_size: int = 60, width: int = 125, height: int = 125, roundness: int = 1):

        self.position = pos
        self.original_position = Vector2(pos.x, pos.y)  # Save original position
        self.text = text
        self.roundness = roundness
        self.width = width
        self.height = height
        self.original_width = self.width  # Save original width
        self.original_height = self.height  # Save original height
        self.color = fade(RAYWHITE, 0.5)
        self.hovered_color = WHITE
        self.text_color = MATTE_BLACK
        self.font = font
        self.font_size = font_size
        self.original_font_size = self.font_size  # Save original font size

        self.hovered_size = Vector2(1, 1)
        self.hovered_pos = Vector2((self.position.x + self.width / 2), (self.position.y + self.height / 2))

        self.is_being_clicked = False  # Track clicking state

        self.is_active = False # for modes

    def draw(self, is_shrinking=False, is_expanding=False):
        current_width = self.width
        current_height = self.height
        current_position = Vector2(self.position.x, self.position.y)
        current_font_size = self.font_size

        if (self.is_hovered() and is_mouse_button_down(MouseButton.MOUSE_BUTTON_LEFT)) or self.is_active:
            self.is_being_clicked = True
            if not self.is_active: 
                current_width = self.width - 5
                current_height = self.height - 5
                current_font_size = int(self.original_font_size * 0.9)  # Reduce font size by 10%
            else:
                current_width = self.width 
                current_height = self.height 
                current_font_size = self.original_font_size 
            current_position.x = self.position.x + (self.width - current_width) / 2
            current_position.y = self.position.y + (self.height - current_height) / 2
        else:
            self.is_being_clicked = False

        rec = Rectangle(current_position.x, current_position.y, current_width, current_height)
        draw_rectangle_rounded(rec, self.roundness, 0, self.color)

        hover_width = self.hovered_size.x if not self.is_being_clicked else current_width
        hover_height = self.hovered_size.y if not self.is_being_clicked else current_height
        hover_x = self.hovered_pos.x if not self.is_being_clicked else current_position.x + (current_width - hover_width) / 2
        hover_y = self.hovered_pos.y if not self.is_being_clicked else current_position.y + (current_height - hover_height) / 2

        if self.is_hovered() or self.is_being_clicked:
            draw_rectangle_rounded(Rectangle(hover_x, hover_y, hover_width, hover_height), self.roundness, 0, self.hovered_color)
            if not self.is_being_clicked:
                self.hovered_size = vector2_add(self.hovered_size, vector2_scale(Vector2(HOVERED_REC_EXPAND_SPEED, HOVERED_REC_EXPAND_SPEED), get_frame_time()))
                self.hovered_size = vector2_clamp(self.hovered_size, Vector2(1, 1), Vector2(self.width, self.width))
                self.hovered_pos = vector2_subtract(self.hovered_pos, vector2_scale(Vector2(HOVERED_REC_EXPAND_SPEED / 2, HOVERED_REC_EXPAND_SPEED / 2), get_frame_time()))
                self.hovered_pos = vector2_clamp(self.hovered_pos, self.position, Vector2(self.position.x + self.width / 2, self.position.y + self.height / 2))
        else:
            self.hovered_size = vector2_subtract(self.hovered_size, vector2_scale(Vector2(HOVERED_REC_EXPAND_SPEED, HOVERED_REC_EXPAND_SPEED), get_frame_time()))
            self.hovered_size = vector2_clamp(self.hovered_size, Vector2(1, 1), Vector2(self.width, self.height))
            self.hovered_pos = vector2_add(self.hovered_pos, vector2_scale(Vector2(HOVERED_REC_EXPAND_SPEED / 2, HOVERED_REC_EXPAND_SPEED / 2), get_frame_time()))
            self.hovered_pos = vector2_clamp(self.hovered_pos, self.position, Vector2(self.position.x + self.width / 2, self.position.y + self.height / 2))

        text_size = measure_text_ex(self.font, self.text, current_font_size, 0)
        text_x = current_position.x + (current_width - text_size.x) / 2
        text_y = current_position.y + (current_height - text_size.y) / 2

        if self.text == "/" and not is_shrinking and not is_expanding:
            draw_text("÷", int(text_x - 3), int(text_y - 1), current_font_size + 15, self.text_color)
        elif not is_shrinking and not is_expanding: 
            draw_text_ex(self.font, self.text, Vector2(text_x, text_y), current_font_size, 0, self.text_color)

    def is_hovered(self):
        mouse_pos = get_mouse_position()
        return check_collision_point_rec(mouse_pos, Rectangle(self.position.x, self.position.y, self.width, self.height))

    def is_clicked(self):
        return is_mouse_button_pressed(MouseButton.MOUSE_BUTTON_LEFT) and self.is_hovered()




BUTTONS_FLIPPING_SPEED = 750

font_data = bytes(font_hex)
font_data_italic = bytes(font_hex_italic)

class Window:


    def __init__(self, width, height, title):

        set_config_flags(ConfigFlags.FLAG_VSYNC_HINT)
        init_window(width, height, title.encode())
        set_target_fps(60)        

        self.target = load_render_texture(APP_WIDTH, APP_HEIGHT)
        set_texture_filter(self.target.texture, TextureFilter.TEXTURE_FILTER_BILINEAR)

        self.camera = Camera2D(
            Vector2(360, 240),
            Vector2(360, 240),
            0.0,
            1.0
        )
      
        with open("vertex_shader.glsl", "w") as f:
            f.write(vertex_shader_code)
        with open("fragment_shader.glsl", "w") as f:
            f.write(fragment_shader_code)


        self.shader = load_shader("vertex_shader.glsl".encode(), "fragment_shader.glsl".encode())

        resolution = (get_screen_width(), get_screen_height())
        resolution_ptr = ffi.new("float[2]", resolution)
        set_shader_value(self.shader, get_shader_location(self.shader, b"resolution"), resolution_ptr, ShaderUniformDataType.SHADER_UNIFORM_VEC2)   

        self.font = load_font_ex("Cubano.ttf", 320, None, 0)
        # self.font = load_font_from_memory(".ttf", font_data, len(font_data), 320, None, 0)
        self.fontItalic = load_font_ex("Poppins-SemiBoldItalic.ttf", 320, None, 0)
        # self.fontItalic = load_font_from_memory(".ttf", font_data_italic, len(font_data_italic), 320, None, 0)

        self.buttons = {
            "1" : Button(Vector2(88, 500), "1", self.font),
            "2" : Button(Vector2(238, 500), "2", self.font),
            "3" : Button(Vector2(388, 500), "3", self.font),
            "4" : Button(Vector2(88, 650), "4", self.font),
            "5" : Button(Vector2(238, 650), "5", self.font),
            "6" : Button(Vector2(388, 650), "6", self.font),
            "7" : Button(Vector2(88, 800), "7", self.font),
            "8" : Button(Vector2(238, 800), "8", self.font),
            "9" : Button(Vector2(388, 800), "9", self.font),
            "0" : Button(Vector2(238, 950), "0", self.font),
            "DX" : Button(Vector2(88, 350), "DX", self.font, font_size=45),
            "DY" : Button(Vector2(238, 350), "DY", self.font, font_size=45),
            "Del" : Button(Vector2(388, 350), "Del", self.font, font_size=45),
            "/" : Button(Vector2(538, 350), "/", self.font),
            "*" : Button(Vector2(538, 500), "x", self.font, font_size=50),
            "-" : Button(Vector2(538, 650), "-", self.font),
            "+" : Button(Vector2(538, 800), "+", self.font),
            "C" : Button(Vector2(388, 950), "C", self.font),
        }

        self.next_buttons = {
            "x" : Button(Vector2(88, 350), "x", self.font, font_size=45),
            "y" : Button(Vector2(238, 350), "y", self.font, font_size=45),
            "(" : Button(Vector2(388, 350), "(", self.font),
            ")" : Button(Vector2(538, 350), ")", self.font),

            "sin" : Button(Vector2(88, 500), "sin", self.font, font_size=45),
            "cos" : Button(Vector2(238, 500), "cos", self.font, font_size=45),
            "tan" : Button(Vector2(388, 500), "tan", self.font, font_size=45),

            "cot" : Button(Vector2(88, 650), "cot", self.font, font_size=45),
            "sec" : Button(Vector2(238, 650), "sec", self.font, font_size=45),
            "csc" : Button(Vector2(388, 650), "csc", self.font, font_size=45),

            "ln" : Button(Vector2(88, 800), "ln", self.font, font_size=45),
            "log" : Button(Vector2(238, 800), "log", self.font, font_size=45),
            "exp" : Button(Vector2(388, 800), "exp", self.font, font_size=45),

            "pi" : Button(Vector2(538, 500), "pi", self.font, font_size=45),
            "e" : Button(Vector2(538, 650), "e", self.font, font_size=45),
            "**" : Button(Vector2(538, 800), "sqrt", self.font, font_size=45),

            "." : Button(Vector2(238, 950), ".", self.font),
            "Del" : Button(Vector2(388, 950), "Del", self.font, font_size=45),
        }
     

        self.button_modes = {
            "BASE" : Button(Vector2(95, 95), "B", self.font, font_size=35, width=50, height=50, roundness=0.5),
            "INVERSE" : Button(Vector2(155, 95), "A", self.font, font_size=35, width=50, height=50, roundness=0.5),
            "HYPERBOLA" : Button(Vector2(215, 95), "H", self.font, font_size=35, width=50, height=50, roundness=0.5),

            "HOMO" : Button(Vector2(550, 95), "H", self.font, font_size=35, width=50, height=50, roundness=0.5),
            "EXACT" : Button(Vector2(610, 95), "E", self.font, font_size=35, width=50, height=50, roundness=0.5),
        }

        self.button_modes["HOMO"].is_active = True
        self.button_modes["BASE"].is_active = True

        # special buttons
        self.more_button = Button(Vector2(88, 950), "...", self.font)
        self.equal_button = Button(Vector2(538, 950), "=", self.font)

        self.equal_button.color = fade(GOLDEN_YELLOW, 0.5)

        # buttons flipping animation
        self.is_buttons_shriking = False
        self.is_buttons_expanding = False

        self.in_base_page = True

        self.input = ""

    def draw_contents(self):

        if is_key_down(KeyboardKey.KEY_RIGHT):
            self.camera.offset.x -= 2

        elif is_key_down(KeyboardKey.KEY_LEFT):
            self.camera.offset.x += 2
       
        draw_rectangle_rounded(Rectangle(50, 75, 650, 1050), 0.1, 0, fade(MATTE_BLACK, 0.15))
        # draw_rectangle_rounded(Rectangle(50, 75, 650, 1050), 0.1, 0, fade(RAYWHITE, 0.45))

        if self.in_base_page:
            for key, button in self.buttons.items():
                if button.is_clicked():
                    self.input += key
                            
                            
                button.draw(self.is_buttons_shriking, self.is_buttons_expanding)

            # buttons flipping animation
            if all(button.width <= 0 for button in self.buttons.values()) and not self.is_buttons_expanding:
                self.is_buttons_shriking = False
                self.is_buttons_expanding = True

            if all(button.width >= 125 for button in self.buttons.values()) and not self.is_buttons_shriking and self.is_buttons_expanding:
                self.is_buttons_expanding = False
                self.in_base_page = not self.in_base_page

        else:
            for key, button in self.next_buttons.items():
                if button.is_clicked():
                    match key:
                        case "Del":
                            self.input = self.input[:-1]
                            pass

                button.draw(self.is_buttons_shriking, self.is_buttons_expanding)

            # buttons flipping animation too
            if all(button.width <= 0 for button in self.next_buttons.values()) and not self.is_buttons_expanding:
                self.is_buttons_shriking = False
                self.is_buttons_expanding = True

            if all(button.width >= 125 for button in self.next_buttons.values()) and not self.is_buttons_shriking and self.is_buttons_expanding:
                self.is_buttons_expanding = False
                self.in_base_page = not self.in_base_page

        for key, button in self.button_modes.items():
                if button.is_clicked():
                    match key:
                        case "BASE":
                            button.is_active = True
                            self.button_modes["INVERSE"].is_active = False
                            self.button_modes["HYPERBOLA"].is_active = False
                        case "INVERSE":
                            button.is_active = True
                            self.button_modes["BASE"].is_active = False
                            self.button_modes["HYPERBOLA"].is_active = False
                        case "HYPERBOLA":
                            button.is_active = True
                            self.button_modes["BASE"].is_active = False
                            self.button_modes["INVERSE"].is_active = False

                        case "HOMO":
                            button.is_active = True
                            self.button_modes["EXACT"].is_active = False

                        case "EXACT":
                            button.is_active = True
                            self.button_modes["HOMO"].is_active = False
                
                button.draw()

        # buttons flipping animation too too
        if self.is_buttons_shriking and not self.is_buttons_expanding:
            for button in self.buttons.values() if self.in_base_page else self.next_buttons.values():
                button.width -= int(BUTTONS_FLIPPING_SPEED * get_frame_time())
                button.position.x += int(BUTTONS_FLIPPING_SPEED / 2 * get_frame_time())

        if self.is_buttons_expanding and not self.is_buttons_shriking:
            for button in self.buttons.values() if self.in_base_page else self.next_buttons.values(): 
                button.width += int(BUTTONS_FLIPPING_SPEED * get_frame_time())
                button.position.x -= int(BUTTONS_FLIPPING_SPEED / 2 * get_frame_time())


        self.more_button.draw()
        self.equal_button.draw()

        if self.more_button.is_clicked():
            if not self.is_buttons_shriking and not self.is_buttons_expanding:
                self.is_buttons_shriking = True


        
        screen_rect = Rectangle(100, 165, 550, 150)
        draw_rectangle_rounded(screen_rect, 0.1, 0, fade(MATTE_BLACK, 0.1))

        # Begin scissor mode to clip text outside the rectangle bounds
        begin_scissor_mode(int(screen_rect.x), int(screen_rect.y), int(screen_rect.width), int(screen_rect.height))

        # Use Camera2D to handle text scrolling
        begin_mode_2d(self.camera)

        # Measure the width of the full input text
        text_width = measure_text_ex(self.font, self.input, 85, 0).x
        max_visible_width = screen_rect.width - 30  # Leave padding on the sides

        # Dynamically adjust the text position
        if text_width <= max_visible_width:
            # Text fits within the screen: Align to the right
            text_x = screen_rect.x + screen_rect.width - 30 - text_width
        else:
            # Text overflows: Move the text to the left as it grows
            overflow_offset = text_width - max_visible_width  # Calculate overflow offset
            text_x = screen_rect.x + screen_rect.width - 30 - max_visible_width - overflow_offset

        # Draw the text at the calculated position
        draw_text_ex(self.font, self.input, Vector2(text_x, 230), 85, 0, MATTE_BLACK)

        end_mode_2d()

        # End scissor mode
        end_scissor_mode()



    def run(self):

        while not window_should_close():
        
            i_time = get_time()
            set_shader_value(self.shader, get_shader_location(self.shader, b"iTime"), ffi.new("float[1]", [i_time]), ShaderUniformDataType.SHADER_UNIFORM_FLOAT)

            scale = min(get_screen_width() / APP_WIDTH, get_screen_height() / APP_HEIGHT)
            mouse = get_mouse_position()
            virtual_mouse = vector2_zero()
            virtual_mouse.x = (mouse.x - (get_screen_width() - APP_WIDTH * scale) * 0.5) / scale
            virtual_mouse.y = (mouse.y - (get_screen_height() - APP_HEIGHT * scale) * 0.5) / scale
            virtual_mouse = vector2_clamp(virtual_mouse, vector2_zero(), Vector2(APP_WIDTH, APP_HEIGHT))
            set_mouse_offset(int(-(get_screen_width() - (APP_WIDTH * scale)) * 0.5), int(-(get_screen_height() - (APP_HEIGHT * scale)) * 0.5))
            set_mouse_scale(1 / scale, 1 / scale)
      
            begin_texture_mode(self.target)
            clear_background(WHITE)

            begin_shader_mode(self.shader)
            draw_rectangle(0, 0, APP_WIDTH, APP_HEIGHT, WHITE)
            end_shader_mode()
            self.draw_contents()
            end_texture_mode()

            begin_drawing()
            clear_background(WHITE)
            draw_texture_pro(
                self.target.texture, 
                Rectangle(0, 0, APP_WIDTH, -APP_HEIGHT), 
                Rectangle((get_screen_width() - APP_WIDTH * scale) * 0.5, (get_screen_height() - APP_HEIGHT * scale) * 0.5, 
                          APP_WIDTH * scale, APP_HEIGHT * scale), 
                Vector2(0, 0), 
                0, 
                WHITE)
            end_drawing()



    def __del__(self):
        close_window()
        unload_shader(self.shader)
        os.remove("vertex_shader.glsl")
        os.remove("fragment_shader.glsl")



def main():
    app = Window(500, 800, "DE")
    app.run()


if __name__ == "__main__":
    main()