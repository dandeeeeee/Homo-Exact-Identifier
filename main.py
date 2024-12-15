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




class Button:

    def __init__(self, pos: Vector2, text: str, font: Font):

        self.position = pos
        self.text = text
        self.roundness = 0.5
        self.width = 125
        self.height = 125
        self.color = fade(RAYWHITE, 0.5)
        self.hovered_color = WHITE
        self.text_color = MATTE_BLACK
        self.font = font
        self.font_size = 60


    def draw(self, is_shriking = False, is_expanding = False):

        rec = Rectangle(self.position.x, self.position.y, self.width, self.height)
        draw_rectangle_rounded(rec, self.roundness, 0, self.hovered_color if self.is_hovered() else self.color)

        text_size = measure_text_ex(self.font, self.text, self.font_size, 0)
        text_x = self.position.x + (self.width - text_size.x) / 2
        text_y = self.position.y + (self.height - text_size.y) / 2
        if self.text == "/" and not is_shriking and not is_expanding:
            draw_text("÷", int(text_x - 4), int(text_y + 1), self.font_size, self.text_color)
        elif not is_shriking and not is_expanding: 
            draw_text_ex(self.font, self.text, Vector2(text_x, text_y), self.font_size, 0, self.text_color)


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
      
        with open("vertex_shader.glsl", "w") as f:
            f.write(vertex_shader_code)
        with open("fragment_shader.glsl", "w") as f:
            f.write(fragment_shader_code)


        self.shader = load_shader("vertex_shader.glsl".encode(), "fragment_shader.glsl".encode())

        resolution = (get_screen_width(), get_screen_height())
        resolution_ptr = ffi.new("float[2]", resolution)
        set_shader_value(self.shader, get_shader_location(self.shader, b"resolution"), resolution_ptr, ShaderUniformDataType.SHADER_UNIFORM_VEC2)   

        # self.font = load_font_ex("Poppins-SemiBold.ttf", 320, None, 0)
        self.font = load_font_from_memory(".ttf", font_data, len(font_data), 320, None, 0)
        # self.fontItalic = load_font_ex("Poppins-SemiBoldItalic.ttf", 320, None, 0)
        self.fontItalic = load_font_from_memory(".ttf", font_data_italic, len(font_data_italic), 320, None, 0)

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
            "^B" : Button(Vector2(88, 350), "^B", self.font),
            "^2" : Button(Vector2(238, 350), "^2", self.font),
            "Del" : Button(Vector2(388, 350), "Del", self.font),
            "/" : Button(Vector2(538, 350), "/", self.font),
            "x" : Button(Vector2(538, 500), "x", self.font),
            "-" : Button(Vector2(538, 650), "-", self.font),
            "+" : Button(Vector2(538, 800), "+", self.font),
            "C" : Button(Vector2(388, 950), "C", self.font),
        }

        self.next_buttons = {
            "(" : Button(Vector2(88, 350), "(", self.fontItalic),
            ")" : Button(Vector2(238, 350), ")", self.fontItalic),
            ":))" : Button(Vector2(388, 350), ":))", self.fontItalic),
            ":((" : Button(Vector2(538, 350), ":((", self.fontItalic),

            "sin" : Button(Vector2(88, 500), "sin", self.fontItalic),
            "cos" : Button(Vector2(238, 500), "cos", self.fontItalic),
            "tan" : Button(Vector2(388, 500), "tan", self.fontItalic),

            "cot" : Button(Vector2(88, 650), "cot", self.fontItalic),
            "sec" : Button(Vector2(238, 650), "sec", self.fontItalic),
            "csec" : Button(Vector2(388, 650), "csec", self.fontItalic),

            "ln" : Button(Vector2(88, 800), "ln", self.fontItalic),
            "log" : Button(Vector2(238, 800), "log", self.fontItalic),
            "exp" : Button(Vector2(388, 800), "exp", self.fontItalic),

            "pi" : Button(Vector2(538, 500), "pi", self.font),
            "e" : Button(Vector2(538, 650), "e", self.font),
            "sqrt" : Button(Vector2(538, 800), "sqrt", self.font),

            "x" : Button(Vector2(238, 950), "x", self.fontItalic),
            "y" : Button(Vector2(388, 950), "y", self.fontItalic),
        }

        # special buttons
        self.more_button = Button(Vector2(88, 950), "...", self.font)
        self.equal_button = Button(Vector2(538, 950), "=", self.font)

        self.equal_button.color = fade(GOLDEN_YELLOW, 0.5)

        # buttons flipping animation
        self.is_buttons_shriking = False
        self.is_buttons_expanding = False

        self.in_base_page = True

    def draw_contents(self):
       
        draw_rectangle_rounded(Rectangle(50, 75, 650, 1050), 0.1, 0, fade(RAYWHITE, 0.45))

        if self.in_base_page:
            for key, button in self.buttons.items():
                if button.is_clicked():
                    match key:
                        case "...":
                            pass
                            
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
                        case "...":
                            pass

                button.draw(self.is_buttons_shriking, self.is_buttons_expanding)

            # buttons flipping animation too
            if all(button.width <= 0 for button in self.next_buttons.values()) and not self.is_buttons_expanding:
                self.is_buttons_shriking = False
                self.is_buttons_expanding = True

            if all(button.width >= 125 for button in self.next_buttons.values()) and not self.is_buttons_shriking and self.is_buttons_expanding:
                self.is_buttons_expanding = False
                self.in_base_page = not self.in_base_page

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