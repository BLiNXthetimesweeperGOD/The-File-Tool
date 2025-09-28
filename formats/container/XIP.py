#Microsoft Xbox XIP handling functions
#Based on https://github.com/JayFoxRox/UnXiP
from libraries.codingTools import *

def XIP_GetZeroTerminatedString(XIP, offset):
    XIP.seek(offset)
    
    data = b'' #The final, stored data
    value = b'' #What's being read
    
    while value != b'\x00':
        value = XIP.read(1)
        data+=value

    return data.rstrip(b'\x00').decode("UTF-8")

def XIP_ReadHeader(XIP):
    XIP.seek(4, 1) #Magic can be skipped, the main script already checked it
    XIP_DataStart = LE_Unpack.uint(XIP.read(4))
    XIP_FileCount = LE_Unpack.ushort(XIP.read(2))
    XIP_FileNameCount = LE_Unpack.ushort(XIP.read(2))
    XIP_DataBlockSize = LE_Unpack.uint(XIP.read(4))

    return XIP_DataStart, XIP_FileCount, XIP_FileNameCount

def XIP_ReadFileTable(XIP, XIP_DataStart, XIP_FileCount):
    XIP_FileInformation = []
    
    for fileTableIndex in range(XIP_FileCount):
        XIP_FileOffset = LE_Unpack.uint(XIP.read(4))+XIP_DataStart
        XIP_FileLength = LE_Unpack.uint(XIP.read(4))
        XIP_FileFormat = LE_Unpack.uint(XIP.read(4))
        XIP_TimeStamp  = LE_Unpack.uint(XIP.read(4)) #Unused?
        
        XIP_FileInformation.append([XIP_FileOffset, XIP_FileLength, XIP_FileFormat, XIP_TimeStamp])


    return XIP_FileInformation

def XIP_ReadFileNameTable(XIP, XIP_FileNameCount):
    XIP_NameInformation = []
    XIP_FileNames = []
    
    for nameTableIndex in range(XIP_FileNameCount):
        XIP_NameIndex = LE_Unpack.ushort(XIP.read(2))
        XIP_NameOffset = LE_Unpack.ushort(XIP.read(2))

        XIP_NameInformation.append([XIP_NameIndex, XIP_NameOffset])

    XIP_NameListOffset = XIP.tell()
    
    for NameInformation in XIP_NameInformation:
        XIP_FileName = XIP_GetZeroTerminatedString(XIP, NameInformation[1]+XIP_NameListOffset)

        XIP_FileNames.append([XIP_FileName, NameInformation[0]])

    return XIP_FileNames

def XIP_SaveFiles(XIP, XIP_FileInformation, XIP_FileNames, outPath):
    for XIP_Name in XIP_FileNames:
        if XIP_FileInformation[XIP_Name[1]][2] != 4:
            XIP_File = XIP_FileInformation[XIP_Name[1]]
            
            XIP.seek(XIP_File[0])
            
            XIP_FileData = XIP.read(XIP_File[1])

            with open(outPath+XIP_Name[0], "w+b") as output:
                output.write(XIP_FileData)
        else:
            with open(outPath+XIP_Name[0]+".txt", "w+") as output:
                text = f"{hex(XIP_FileInformation[XIP_Name[1]][0])}\n{hex(XIP_FileInformation[XIP_Name[1]][1])}\n{XIP_FileInformation[XIP_Name[1]][2]}\n{XIP_FileInformation[XIP_Name[1]][3]}"
                output.write(text)
        
