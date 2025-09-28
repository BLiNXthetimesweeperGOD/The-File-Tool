#LZSS compression algorithm used by Children of Mana on the Nintendo DS
from libraries.codingTools import *

def decompressLZSS(file):
    currentSize = 0
    bufferIndex = 0
    with open(file, "rb") as lzss:
        lzssReader = BE_BitReader(lzss)
        
        lzss.seek(4, 1) #Skip magic

        versionNumber = lzss.read(4)
        compressedSize = LE_Unpack.uint(lzss.read(4))
        decompressedSize = LE_Unpack.uint(lzss.read(4))
        
        decompressedData = bytearray(decompressedSize)
        
        while currentSize != decompressedSize:
            bit = lzssReader.read(1)
            if bit == 1:
                data = lzssReader.read(8)
                decompressedData[bufferIndex] = data
                
                bufferIndex = (bufferIndex + 1)
                currentSize+=1
            else:
                length = lzssReader.read(8)+3
                offset = lzssReader.read(13)
                source = (bufferIndex - offset - 1)
                for i in range(length):
                    data = decompressedData[source]
                    decompressedData[bufferIndex] = data
                    source = (source + 1)
                    bufferIndex = (bufferIndex + 1)
                    currentSize+=1
                    
        return decompressedData
