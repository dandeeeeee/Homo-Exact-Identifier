with open("Poppins-SemiBoldItalic.ttf", "rb") as font_file:
    font_data = font_file.read()

hex_array = ", ".join(f"0x{byte:02x}" for byte in font_data)

with open("font_hex_italic.py", "w") as output_file:
    output_file.write(f"font_hex_italic = [{hex_array}]")

print("Hexadecimal array saved to font_hex.py")
