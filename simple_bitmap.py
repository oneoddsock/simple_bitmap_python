class SimpleBitmap:
    """Simple bitmap class to generate BMP files."""
    
    width = 0
    height = 0
    withAlpha = False
    bitmap = []

    def __init__(self, width, height, withAlpha = False):
        self.width = width
        self.height = height
        self.withAlpha = withAlpha
        self.bitmap = [0] * (width * height)

    def __fix_value(self, value):
        return max(0, min(255, int(value)))
    
    def set_pixel(self, x, y, r, g, b, a = 255):
        """Set the pixel at (x, y) to the given color as (r, g, b, a)."""
        self.bitmap[y * self.width + x] = (self.__fix_value(r), self.__fix_value(g), self.__fix_value(b), self.__fix_value(a))

    def get_pixel(self, x, y):
        """Get the color of the pixel at (x, y) as (r, g, b, a)."""
        return self.bitmap[y * self.width + x]

    def __copy_bytes(self, dest, offset, src):
        for i in range(len(src)):
            dest[offset + i] = src[i]

    def __get_unique_color_count(self):
        map = {}
        for y in range(self.height):
            for x in range(self.width):
                pixel = self.get_pixel(x, y)
                pixelValue = pixel[3] + pixel[2] * 256 + pixel[1] * 256 * 256 + pixel[0] * 256 * 256 * 256
                if pixelValue in map:
                    map[pixelValue] += 1
                else:
                    map[pixelValue] = 1
        return len(map)
    
    def get_image(self):
        """Generates the image as a bitmap."""
        stride = (self.width * 3 + 3) & ~3
        bitsPerPixel = 24
        compression = 0 # BI_RGB -- no compression
        extraBytes = 0
        if self.withAlpha:
            stride = self.width * 4
            bitsPerPixel = 32
            compression = 6 # BI_ALPHABITFIELDS
            extraBytes = 16
        dibSize = 40
        pixelOffset = 14 + dibSize + extraBytes
        size = pixelOffset + self.height * stride
        planes = 1
        zero = 0
        pixPerMeter = 2835

        result = bytearray(size)

        # Bitmap file header 
        self.__copy_bytes(result, 0, [0x42, 0x4D]) # BM
        self.__copy_bytes(result, 2, size.to_bytes(4, 'little')) # File size
        self.__copy_bytes(result, 6, [0, 0, 0, 0]) # Reserved
        self.__copy_bytes(result, 10, pixelOffset.to_bytes(4, 'little'))

        # DIB header
        self.__copy_bytes(result, 14, dibSize.to_bytes(4, 'little'))
        self.__copy_bytes(result, 18, self.width.to_bytes(4, 'little'))
        self.__copy_bytes(result, 22, (-self.height).to_bytes(4, 'little', signed=True)) # Negative height for top-down bitmap
        self.__copy_bytes(result, 26, planes.to_bytes(2, 'little')) # Planes
        self.__copy_bytes(result, 28, bitsPerPixel.to_bytes(2, 'little'))
        self.__copy_bytes(result, 30, zero.to_bytes(4, 'little')) # Compression BI_RGB -- no compression
        self.__copy_bytes(result, 34, zero.to_bytes(4, 'little')) # Image size -- can use 0 for BI_RGB
        self.__copy_bytes(result, 38, pixPerMeter.to_bytes(4, 'little')) # X pixels per meter
        self.__copy_bytes(result, 42, pixPerMeter.to_bytes(4, 'little')) # Y pixels per meter
        self.__copy_bytes(result, 46, self.__get_unique_color_count().to_bytes(4, 'little')) # Colors used
        self.__copy_bytes(result, 50, zero.to_bytes(4, 'little')) # Important colors

        # Alpha mask
        if self.withAlpha:
            # From https://learn.microsoft.com/en-us/previous-versions/windows/embedded/aa452885(v=msdn.10)?redirectedfrom=MSDN for BI_ALPHABITFIELDS
            rgbaMask = [0x000000FF, 0x0000FF00, 0x00FF0000, 0xFF000000] # ARGB order
            for mask in rgbaMask:
                self.__copy_bytes(result, 54, mask.to_bytes(4, 'little'))
        
        # Pixel data
        bytesPerPixel = bitsPerPixel // 8
        for y in range(self.height):
            for x in range(self.width):
                (r, g, b, a) = self.get_pixel(x, y)
                offset = pixelOffset + y * stride + x * bytesPerPixel
                result[offset] = b
                result[offset + 1] = g
                result[offset + 2] = r
                if self.withAlpha:
                    result[offset + 3] = a

        return result

    def __str__(self):
        result = ''
        for y in range(self.height):
            for x in range(self.width):
                result += '*' if self.get_pixel(x, y) else ' '
            result += '\n'
        return