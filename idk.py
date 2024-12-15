import os
from pyray import *
from raylib import ffi



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



APP_WIDTH = 1920
APP_HEIGHT = 1080  

MATTE_BLACK = Color(51, 51, 51, 255)
GOLDEN_YELLOW = Color(255, 223, 0, 255)



class Window:


    def __init__(self, width, height, title):

        set_config_flags(ConfigFlags.FLAG_VSYNC_HINT | ConfigFlags.FLAG_MSAA_4X_HINT)
        init_window(width, height, title.encode())
        set_target_fps(60)        
      
        with open("vertex_shader.glsl", "w") as f:
            f.write(vertex_shader_code)
        with open("fragment_shader.glsl", "w") as f:
            f.write(fragment_shader_code)

        
        self.shader = load_shader("vertex_shader.glsl".encode(), "fragment_shader.glsl".encode())

        resolution = (get_screen_width(), get_screen_height())
        resolution_ptr = ffi.new("float[2]", resolution)
        set_shader_value(self.shader, get_shader_location(self.shader, b"resolution"), resolution_ptr, ShaderUniformDataType.SHADER_UNIFORM_VEC2)
    
    

    def draw_contents(self):
       
        draw_rectangle_rounded(Rectangle(30, 50, 440, 700), 0.1, 0, fade(WHITE, 0.5))



    def run(self):

        while not window_should_close():
        
            i_time = get_time()
            set_shader_value(self.shader, get_shader_location(self.shader, b"iTime"), ffi.new("float[1]", [i_time]), ShaderUniformDataType.SHADER_UNIFORM_FLOAT)

      
            begin_drawing()
            clear_background(WHITE)

            begin_shader_mode(self.shader)
            draw_rectangle(0, 0, get_screen_width(), get_screen_height(), WHITE)
            end_shader_mode()

            self.draw_contents()
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
