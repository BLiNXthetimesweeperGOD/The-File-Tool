#Microsoft Xbox .XBX image extractor
from libraries.codingTools import *
from formats.image.DXT import *
from formats.swizzle.swizzle_morton import * #This is the Xbox swizzle from ReverseBox

def XBX_ReadHeader(XBX):
    XBX_CompressionTypes = {
        0x6:"Swizzled BGRA8888",
        0xC:"DXT1",
        0xE:"DXT3"
        }

    XBX_ImageSizes = {
        0x0:1, #Likely unused
        0x1:2, #Likely unused
        0x2:4,
        0x3:8,
        0x4:16,
        0x5:32,
        0x6:64, #Everything before this is a guess
        0x7:128,
        0x8:256,
        0x9:512,
        0xA:1024,
        0xB:2048,
        0xC:4096,
        0xD:8192,
        0xE:16384,
        0xF:32768
        }
    
    XBX.seek(4, 1) #Skip magic (it was already checked)
    XBX_Size = LE_Unpack.uint(XBX.read(4))
    XBX_ImageDataStartOffset = LE_Unpack.uint(XBX.read(4))

    XBX_ImageDataLength = XBX_Size-XBX_ImageDataStartOffset

    #The purpose of these would be great to have
    XBX_Unknown1 = LE_Unpack.ushort(XBX.read(2)) #File count?
    XBX_Unknown2 = LE_Unpack.ushort(XBX.read(2)) #File type?

    XBX.seek(8, 1) #Skip padding

    XBX_ParamBytes = XBX.read(4)

    #Obtain the known parameters
    XBX_CompressionType = XBX_CompressionTypes[XBX_ParamBytes[1] & 0x0F]
    XBX_XSize = XBX_ImageSizes[XBX_ParamBytes[2] >> 4]
    XBX_YSize = XBX_ImageSizes[XBX_ParamBytes[3] & 0x0F]

    return XBX_ImageDataStartOffset, XBX_ImageDataLength, XBX_CompressionType, XBX_XSize, XBX_YSize

def XBX_ConvertImage(XBX, XBX_ImageDataStartOffset, XBX_ImageDataLength, XBX_CompressionType, XBX_XSize, XBX_YSize):
    pixels = []
    
    XBX.seek(XBX_ImageDataStartOffset)

    XBX_ImageData = XBX.read(XBX_ImageDataLength)

    if XBX_CompressionType == "DXT1":
        decompressedData = bytearray(pixelsToBytes(decompressDxt1(XBX_ImageData, XBX_XSize, XBX_YSize)))
        for index in range(len(decompressedData)//4):
            pixel = decompressedData[index*4:(index*4)+4]
            r = pixel[0]
            g = pixel[1]
            b = pixel[2]
            a = pixel[3]
            pixels.append((r, g, b, a))
            
    elif XBX_CompressionType == "DXT3":
        XBX_ImageData = XBX_ImageData[:XBX_XSize*XBX_YSize]
        decompressedData = bytearray(pixelsToBytes(decompressDxt3(XBX_ImageData, XBX_XSize, XBX_YSize)))
        for index in range(len(decompressedData)//4):
            pixel = decompressedData[index*4:(index*4)+4]
            r = pixel[0]
            g = pixel[1]
            b = pixel[2]
            a = pixel[3]
            pixels.append((r, g, b, a))
            
    elif XBX_CompressionType == "DXT5": #Haven't come across this one yet actually, so it isn't fully implemented
        decompressedData = bytearray(pixelsToBytes(decompressDxt5(XBX_ImageData, XBX_XSize, XBX_YSize)))
        for index in range(len(decompressedData)//4):
            pixel = decompressedData[index*4:(index*4)+4]
            r = pixel[0]
            g = pixel[1]
            b = pixel[2]
            a = pixel[3]
            pixels.append((r, g, b, a))

    elif XBX_CompressionType == "Swizzled BGRA8888": #This format is uncompressed, but swizzled
        XBX_Unswizzled = unswizzle_morton(XBX_ImageData, XBX_XSize, XBX_YSize, 32, 1)

        for i in range(0, len(XBX_Unswizzled), 4):
            b = XBX_Unswizzled[i]
            g = XBX_Unswizzled[i + 1]
            r = XBX_Unswizzled[i + 2]
            a = XBX_Unswizzled[i + 3]
            pixels.append((r, g, b, a))

    else:
        print(XBX_ParamBytes[1] & 0x0F) #Useful for finding more formats

    if len(pixels) > 0:
        return pixels

def XBX_SaveImage(pixels, XBX_XSize, XBX_YSize, output):
    with open(output, "w+b") as image:
        image.write(imageData.generateTGA(XBX_XSize, XBX_YSize, pixels))
