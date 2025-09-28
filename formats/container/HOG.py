#Bubsy 3D HOG container handling functions
from libraries.codingTools import *

def HOG_ReadHeader(HOG): #Oink_1.wav
    HOG.seek(4, 1) #Skip the file magic
    HOG_FileCount = LE_Unpack.uint(HOG.read(4))
    HOG_DataStart = LE_Unpack.uint(HOG.read(4))

    return HOG_FileCount, HOG_DataStart

def HOG_ReadFileTable(HOG, HOG_FileCount, HOG_DataStart, HOG_TotalSize): #Oink_2.wav
    HOG_FileEntries = []
    
    for fileIndex in range(HOG_FileCount):
        HOG_FileOffset = LE_Unpack.uint(HOG.read(4))+HOG_DataStart
        HOG_NextEntryOffset = HOG.tell()
        HOG_NextFileOffset = LE_Unpack.uint(HOG.read(4))+HOG_DataStart

        if fileIndex != HOG_FileCount:
            HOG_FileSize = HOG_NextFileOffset - HOG_FileOffset
        else:
            HOG_FileSize = HOG_TotalSize-HOG_FileOffset

        HOG_FileEntries.append([HOG_FileOffset, HOG_FileSize])

        HOG.seek(HOG_NextEntryOffset)

    return HOG_FileEntries

def HOG_SaveFiles(HOG, HOG_FileEntries, outPath): #Oink_3.wav
    index = 0
    for HOG_File in HOG_FileEntries:
        HOG.seek(HOG_File[0])
        HOG_FileData = HOG.read(HOG_File[1])

        if HOG_FileData[0] == 0x10:
            extension = "tim"
        elif HOG_FileData[0] == 0x41:
            extension = "tmd"
        elif HOG_FileData.startswith(b'pQES'):
            extension = "seq"
        elif b'\x00\x00\x00\x00\x04\x03\x00\x20' in HOG_FileData:
            extension = "triList"
        else:
            extension = "bin"

        with open(outPath+f'{index:04}.{extension}', "w+b") as output:
            output.write(HOG_FileData)

        index += 1

