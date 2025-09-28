#BLiNX: the Time Sweeper MIT texture container handling functions
from libraries.codingTools import *

def MIT_ReadHeader(MIT):
    MIT.seek(4, 1) #magic. No need to validate this, we did that earlier.
    MIT_FileCount = LE_Unpack.uint(MIT.read(4))
    MIT_DataStart = LE_Unpack.uint(MIT.read(4))
    MIT.seek(4, 1) #Skip the padding

    return MIT_FileCount, MIT_DataStart

def MIT_ReadFileTable(MIT, MIT_FileCount, MIT_DataStart):
    MIT_FileInfo = []
    
    for MIT_TextureIndex in range(MIT_FileCount):
        MIT_TextureName = (MIT.read(0x28).rstrip(b'\x00')).decode('UTF-8')
        MIT_FileOffset  = LE_Unpack.uint(MIT.read(4)) + MIT_DataStart
        MIT_FileSize    = LE_Unpack.uint(MIT.read(4))

        MIT_FileInfo.append([MIT_TextureName, MIT_FileOffset, MIT_FileSize])
        
    return MIT_FileInfo

def MIT_SaveFiles(MIT, MIT_FileInfo, outPath):
    for MIT_File in MIT_FileInfo:
        MIT.seek(MIT_File[1])
        
        MIT_FileData = MIT.read(MIT_File[2])

        with open(outPath+MIT_File[0], "w+b") as output:
            output.write(MIT_FileData)
    
    
