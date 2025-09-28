#Square Enix RAX container handling functions
from libraries.codingTools import *
from formats.compression.SquareEnixLZSS import *

def RAX_GetZeroTerminatedString(RAX, offset):
    RAX.seek(offset)
    
    RAX_FileName = b'' #The final, stored data
    currentValue = b'' #What's being read
    
    while currentValue != b'\x00':
        currentValue = RAX.read(1)
        RAX_FileName+=currentValue

    return RAX_FileName.rstrip(b'\x00').decode("UTF-8")

def RAX_ReadHeader(RAX): #Hey everyone! Today, I got this expensive phone and -
    RAX.seek(4, 1) #Skip magic
    RAX_FileCount = LE_Unpack.uint(RAX.read(4))
    RAX_FileNameTableLength = LE_Unpack.uint(RAX.read(4))
    RAX_ContainerSize = LE_Unpack.uint(RAX.read(4))
    
    #Some additional variables are needed...
    RAX_NameTableStart = (RAX_FileCount*16)+16
    RAX_DataStart = RAX_NameTableStart+RAX_FileNameTableLength
    

    return RAX_FileCount, RAX_NameTableStart, RAX_DataStart

def RAX_ReadFileTable(RAX, RAX_FileCount, RAX_NameTableStart, RAX_DataStart):
    RAX_FileInfo = []

    for fileIndex in range(RAX_FileCount):
        #This additional extension isn't needed for extraction
        RAX_FileExtension = (RAX.read(4).rstrip(b'\x00')).decode("UTF-8")
        RAX_FileNameOffset = LE_Unpack.uint(RAX.read(4))+RAX_NameTableStart
        RAX_FileDataOffset = LE_Unpack.uint(RAX.read(4))+RAX_DataStart
        RAX_FileSize = LE_Unpack.uint(RAX.read(4))

        RAX_FileInfo.append([RAX_FileExtension, RAX_FileNameOffset, RAX_FileDataOffset, RAX_FileSize])

    return RAX_FileInfo

def RAX_GetFileNames(RAX, RAX_FileInfo):
    RAX_FileNames = []
    
    for RAX_Info in RAX_FileInfo:
        RAX_FileName = RAX_GetZeroTerminatedString(RAX, RAX_Info[1])

        print(RAX_FileName)
        RAX_FileNames.append(RAX_FileName)

    return RAX_FileNames

def RAX_SaveFiles(RAX, RAX_FileInfo, RAX_FileNames, outPath):
    nameIndex = 0
    for RAX_Info in RAX_FileInfo:
        if not os.path.exists(outPath+fileTools.folder(RAX_FileNames[nameIndex])):
            os.makedirs(outPath+fileTools.folder(RAX_FileNames[nameIndex]))
        RAX.seek(RAX_Info[2])
        RAX_FileData = RAX.read(RAX_Info[3])

        if RAX_FileData.startswith(b'LZSS'): #Decompress the file data
            with open("working.bin", "w+b") as RAX_Decompress:
                RAX_Decompress.write(RAX_FileData)

        RAX_FileData = decompressLZSS("working.bin")

        with open(outPath+RAX_FileNames[nameIndex], "w+b") as output:
            output.write(RAX_FileData)

        nameIndex+=1
        

