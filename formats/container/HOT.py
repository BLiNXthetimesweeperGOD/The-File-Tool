#Voodoo Vince Remastered HOT container handling functions
from libraries.codingTools import *

def HOT_GetZeroTerminatedString(HOT, offset):
    HOT.seek(offset)
    
    data = b'' #The final, stored data
    value = b'' #What's being read
    
    while value != b'\x00':
        value = HOT.read(1)
        data+=value

    return data.rstrip(b'\x00').decode("UTF-8")

def HOT_ReadHeader(HOT): #Plese turn on the air conditner
    HOT.seek(4, 1) #Skip the magic because we've obtained it already
    HOT_VersionNumber = LE_Unpack.uint(HOT.read(4))
    HOT_FileHeaderDataStart = LE_Unpack.uint(HOT.read(4))
    HOT_FileDataStart = LE_Unpack.uint(HOT.read(4))
    HOT_SizeOfEntireFile = LE_Unpack.uint(HOT.read(4))
    HOT_StartOfFileNameTable = LE_Unpack.uint(HOT.read(4))
    HOT_FileCount = LE_Unpack.uint(HOT.read(4))

    HOT.seek(4, 1) #Skip padding

    return HOT_StartOfFileNameTable, HOT_FileCount

def HOT_ReadFileTable(HOT, HOT_StartOfFileNameTable, HOT_FileCount):
    HOT_FileEntries = []
    
    for fileEntry in range(HOT_FileCount-1):
        HOT.seek(4, 1) #Skip padding
        HOT_FileHeaderSize = LE_Unpack.uint(HOT.read(4))
        HOT_FileHeaderOffset = LE_Unpack.uint(HOT.read(4))
        HOT_FileDataSize = LE_Unpack.uint(HOT.read(4))
        HOT.seek(4, 1) #Skip padding
        HOT_FileDataOffset = LE_Unpack.uint(HOT.read(4))
        HOT.seek(4, 1)
        HOT_FileNameOffset = LE_Unpack.uint(HOT.read(4))+HOT_StartOfFileNameTable

        HOT_FileEntries.append([HOT_FileHeaderOffset,
                               HOT_FileHeaderSize,
                               HOT_FileDataOffset,
                               HOT_FileDataSize,
                               HOT_FileNameOffset])

    return HOT_FileEntries

def HOT_GetFileNames(HOT, HOT_FileEntries):
    HOT_FileNames = []

    for HOT_FileEntry in HOT_FileEntries:
        HOT_FileName = HOT_GetZeroTerminatedString(HOT, HOT_FileEntry[4])

        HOT_FileNames.append(HOT_FileName)

    return HOT_FileNames

def HOT_ReconstructFile(HOT, HOT_FileHeaderOffset, HOT_FileHeaderSize, HOT_FileDataOffset, HOT_FileDataSize):
    HOT.seek(HOT_FileHeaderOffset)
    HOT_FileHeaderData = HOT.read(HOT_FileHeaderSize)
    HOT.seek(HOT_FileDataOffset)
    HOT_FileData = HOT.read(HOT_FileDataSize)

    return HOT_FileHeaderData+HOT_FileData

def HOT_SaveFiles(HOT, HOT_FileNames, HOT_FileEntries, outPath):
    fileIndex = 0
    
    for HOT_File in HOT_FileEntries:
        HOT_FileData = HOT_ReconstructFile(HOT, HOT_File[0], HOT_File[1], HOT_File[2], HOT_File[3])

        with open(outPath+HOT_FileNames[fileIndex], "w+b") as output:
            output.write(HOT_FileData)

        fileIndex+=1
