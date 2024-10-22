class SimpleBitmap:
    """Simple bitmap class to generate BMP files."""
    
    width = 0
    height = 0
    withAlpha = False
    bmp = None
    stride = 0
    bytesPerPixel = 0
    pixelOffset = 0

    def __init__(self, width, height, withAlpha = False):
        self.width = width
        self.height = height
        self.withAlpha = withAlpha
        self.stride = (self.width * 3 + 3) & ~3

        dibSize = 40 # BITMAPINFOHEADER
        bitsPerPixel = 24
        extraBytes = 0

        if self.withAlpha:
            dibSize = 56 # BITMAPV3INFOHEADER
            self.stride = self.width * 4
            bitsPerPixel = 32
            extraBytes = 16

        self.pixelOffset = 14 + dibSize + extraBytes
        self.bytesPerPixel = bitsPerPixel // 8

        self.__init_bmp(dibSize, bitsPerPixel)

    def __fix_value(self, value):
        return max(0, min(255, int(value)))
    
    def set_pixel(self, x, y, r, g, b, a = 255):
        """Set the pixel at (x, y) to the given color as (r, g, b, a)."""
        assert x >= 0 and x < self.width
        assert y >= 0 and y < self.height
        offset = self.pixelOffset + y * self.stride + x * self.bytesPerPixel
        # The ordering seems odd, but it is because the pixel data is stored as ARGB in little endian, so it serializes as BGRA.
        self.bmp[offset] = self.__fix_value(b)
        self.bmp[offset + 1] = self.__fix_value(g)
        self.bmp[offset + 2] = self.__fix_value(r)
        if self.withAlpha:
            self.bmp[offset + 3] = self.__fix_value(a)

    def get_pixel(self, x, y):
        """Get the color of the pixel at (x, y) as (r, g, b, a)."""
        assert x >= 0 and x < self.width
        assert y >= 0 and y < self.height
        offset = self.pixelOffset + y * self.stride + x * self.bytesPerPixel
        b = self.bmp[offset]
        g = self.bmp[offset + 1]
        r = self.bmp[offset + 2]
        a = 255
        if self.withAlpha:
            a = self.bmp[offset + 3]
        return (r, g, b, a)

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
    
    def __init_bmp(self, dibSize, bitsPerPixel):
        planes = 1
        zero = 0
        pixPerMeter = 2835
        size = self.pixelOffset + self.height * self.stride

        self.bmp = bytearray(size)

        # Bitmap file header 
        self.__copy_bytes(self.bmp, 0, [0x42, 0x4D]) # BM
        self.__copy_bytes(self.bmp, 2, size.to_bytes(4, 'little')) # File size
        self.__copy_bytes(self.bmp, 6, [0, 0, 0, 0]) # Reserved
        self.__copy_bytes(self.bmp, 10, self.pixelOffset.to_bytes(4, 'little'))

        # DIB header
        self.__copy_bytes(self.bmp, 14, dibSize.to_bytes(4, 'little'))
        self.__copy_bytes(self.bmp, 18, self.width.to_bytes(4, 'little'))
        self.__copy_bytes(self.bmp, 22, (-self.height).to_bytes(4, 'little', signed=True)) # Negative height for top-down bitmap
        self.__copy_bytes(self.bmp, 26, planes.to_bytes(2, 'little')) # Planes
        self.__copy_bytes(self.bmp, 28, bitsPerPixel.to_bytes(2, 'little'))
        self.__copy_bytes(self.bmp, 30, zero.to_bytes(4, 'little')) # Compression BI_RGB -- no compression
        self.__copy_bytes(self.bmp, 34, zero.to_bytes(4, 'little')) # Image size -- can use 0 for BI_RGB
        self.__copy_bytes(self.bmp, 38, pixPerMeter.to_bytes(4, 'little')) # X pixels per meter
        self.__copy_bytes(self.bmp, 42, pixPerMeter.to_bytes(4, 'little')) # Y pixels per meter
        self.__copy_bytes(self.bmp, 46, zero.to_bytes(4, 'little')) # Colors used
        self.__copy_bytes(self.bmp, 50, zero.to_bytes(4, 'little')) # Important colors

        # Alpha mask for V3 header
        if self.withAlpha:
            # From https://upload.wikimedia.org/wikipedia/commons/7/75/BMPfileFormat.svg
            # The mask channels are written in RGBA order.
            # The mask information represents where to find the channel in the data. Since we write the 
            # data as BGRA, the mask information is written as ABGR.
            rgbaMask = [0x0000FF00, 0x00FF0000, 0xFF000000, 0x000000FF] # RGBA order
            for i in range(4):
                mask = rgbaMask[i].to_bytes(4, 'big') # We use big endian here to match the layout on disk.
                self.__copy_bytes(self.bmp, 54 + i * 4, mask)


    def get_image(self):
        """Generates the image as a bitmap."""

        result = bytearray(self.bmp)
        self.__copy_bytes(result, 46, self.__get_unique_color_count().to_bytes(4, 'little'))
        return result

    def __str__(self):
        result = ''
        for y in range(self.height):
            for x in range(self.width):
                result += '*' if self.get_pixel(x, y) else ' '
            result += '\n'
        return