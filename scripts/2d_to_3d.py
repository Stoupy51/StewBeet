
# Imports
from PIL import Image, ImageEnhance

img = Image.open("input.png").convert("RGBA")

thickness = 40
pad = thickness + 60
canvas_w = img.width + pad * 2
canvas_h = img.height + pad * 2

result = Image.new("RGBA", (canvas_w, canvas_h), (0, 0, 0, 0))

# Deep shadow layers
for i in range(thickness, 0, -1):
    factor = i / thickness
    shift_x = -i        # left
    shift_y = -i // 2    # up

    layer = img.copy()
    r, g, b, a = layer.split()
    darkened = ImageEnhance.Brightness(Image.merge("RGB", (r, g, b))).enhance(0.25 + 0.1 * (1 - factor))
    layer = Image.merge("RGBA", (*darkened.split(), a))

    result.paste(layer, (pad + shift_x, pad + shift_y), layer)

# Original image on top
result.paste(img, (pad, pad), img)

# Crop
bbox = result.getbbox()
if bbox:
    m = 20
    bbox = (max(0, bbox[0]-m), max(0, bbox[1]-m),
            min(result.width, bbox[2]+m), min(result.height, bbox[3]+m))
    result = result.crop(bbox)

result.save("output.png", "PNG")
print(f"Done: {result.size}")

