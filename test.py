
import simple_bitmap

imageData = [
    [0, 0, 0, 255, 0, 0, 0],
    [0, 0, 255, 0, 255, 0, 0],
    [0, 255, 0, 0, 0, 255, 0],
    [255, 0, 0, 0, 0, 0, 255],
    [0, 255, 0, 0, 0, 255, 0],
    [0, 0, 255, 0, 255, 0, 0],
    [0, 0, 0, 255, 0, 0, 0],
]

testInfo = [
    {"File": "d:/test_all.bmp", "HasAlpha": False, "Red": True, "Green": True, "Blue": True, "Alpha": False},
    {"File": "d:/test_red.bmp", "HasAlpha": False, "Red": True, "Green": False, "Blue": False, "Alpha": False},
    {"File": "d:/test_green.bmp", "HasAlpha": False, "Red": False, "Green": True, "Blue": False, "Alpha": False},
    {"File": "d:/test_blue.bmp", "HasAlpha": False, "Red": False, "Green": False, "Blue": True, "Alpha": False},

    {"File": "d:/test_alpha_all.bmp", "HasAlpha": False, "Red": True, "Green": True, "Blue": True, "Alpha": False},
    {"File": "d:/test_alpha_red.bmp", "HasAlpha": False, "Red": True, "Green": False, "Blue": False, "Alpha": False},
    {"File": "d:/test_alpha_green.bmp", "HasAlpha": False, "Red": False, "Green": True, "Blue": False, "Alpha": False},
    {"File": "d:/test_alpha_blue.bmp", "HasAlpha": False, "Red": False, "Green": False, "Blue": True, "Alpha": False},
]

for test in testInfo:
    bitmap = simple_bitmap.SimpleBitmap(7, 7, test["HasAlpha"])

    for y in range(bitmap.height):
        for x in range(bitmap.width):
            r = imageData[x][y] if test["Red"] else 0
            g = imageData[x][y] if test["Green"] else 0
            b = imageData[x][y] if test["Blue"] else 0
            a = imageData[x][y] if test["Alpha"] else 255
            bitmap.set_pixel(x, y, r, g, b, a)

    with open(test["File"], 'wb') as f:
        f.write(bitmap.get_image())


bitmap = simple_bitmap.SimpleBitmap(1024, 1024, True)

