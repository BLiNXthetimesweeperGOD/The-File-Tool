#A simple tool for a bunch of file formats with "magic" in their headers
from libraries.codingTools import *

#"NOT ADDED YET" means a script is there, but it has no code yet

#Compression algorithms (for main script only!)
from formats.compression.Yaz0 import * #Nintendo


#Container formats (sorted by game) 
from formats.container.MIT  import * #BLiNX: the Time Sweeper
from formats.container.XSSB import * #BLiNX: the Time Sweeper - NOT ADDED YET

from formats.container.HOG  import * #Bubsy 3D

from formats.container.RAX  import * #Children of Mana

from formats.container.NARC import * #Nintendo - NOT ADDED YET
from formats.container.SARC import * #Nintendo

from formats.container.HOT  import * #Voodoo Vince Remastered - NOT ADDED YET

from formats.container.XIP  import * #Xbox Dashboard


#Image formats
from formats.image.XBX import * #Xbox image file (huge thanks to PatrickHamster for the unswizzling code)


#Open a file dialog that lets the user select multiple files
files = dialogs.files()

for file in files:
    
    with open(file, "rb") as headerCheck: #First, check for easy to handle compression. Decompress the file if needed.
        magic = headerCheck.read(4)
        if magic == b'Yaz0':
            file, magic = decompressYaz0(file)

    outPath = fileTools.folder(file)+"/"+fileTools.nameNoExt(file)+"/"

    if b'\x0C\x22\xEE' in magic: #Bubsy 3D container
        HOG_TotalSize = fileTools.size(file) #Needed for later
        if not os.path.exists(outPath): #Check if the output folder exists. If not, create it.
            os.makedirs(outPath)
        
        with open(file, "rb") as HOG:
            HOG_FileCount, HOG_DataStart = HOG_ReadHeader(HOG)
            HOG_FileEntries = HOG_ReadFileTable(HOG, HOG_FileCount, HOG_DataStart, HOG_TotalSize)

            HOG_SaveFiles(HOG, HOG_FileEntries, outPath)

    elif magic == b'RAX2': #Children of Mana container
        if not os.path.exists(outPath): #Check if the output folder exists. If not, create it.
            os.makedirs(outPath)
            
        with open(file, "rb") as RAX:
            RAX_FileCount, RAX_NameTableStart, RAX_DataStart = RAX_ReadHeader(RAX)
            RAX_FileInfo = RAX_ReadFileTable(RAX, RAX_FileCount, RAX_NameTableStart, RAX_DataStart)
            RAX_FileNames = RAX_GetFileNames(RAX, RAX_FileInfo)

            RAX_SaveFiles(RAX, RAX_FileInfo, RAX_FileNames, outPath)

    elif magic == b'MIT\x00': #BLiNX: the Time Sweeper texture package
        if not os.path.exists(outPath): #Check if the output folder exists. If not, create it.
            os.makedirs(outPath)
            
        with open(file, "rb") as MIT:
            MIT_FileCount, MIT_DataStart = MIT_ReadHeader(MIT)
            MIT_FileInfo = MIT_ReadFileTable(MIT, MIT_FileCount, MIT_DataStart)

            MIT_SaveFiles(MIT, MIT_FileInfo, outPath)
        
    elif magic == b'SARC': #Nintendo SARC/SZS container
        if not os.path.exists(outPath): #Check if the output folder exists. If not, create it.
            os.makedirs(outPath)
            
        with open(file, "rb") as SARC:
            SARC_ValueDecoder, SARC_DataStartOffset = SARC_ReadHeader(SARC)
            SARC_Nodes, SARC_FileNameHashKey = SARC_FileAllocationTable(SARC, SARC_ValueDecoder)
            SARC_FileNames = SARC_FileNameTable(SARC, len(SARC_Nodes))
            
            SARC_SaveFiles(SARC, SARC_Nodes, SARC_FileNames, SARC_FileNameHashKey, SARC_DataStartOffset, outPath)

    elif magic == b'XIP0': #Original Xbox XIP container
        if not os.path.exists(outPath): #Check if the output folder exists. If not, create it.
            os.makedirs(outPath)
            
        with open(file, "rb") as XIP:
            XIP_DataStart, XIP_FileCount, XIP_FileNameCount = XIP_ReadHeader(XIP)
            XIP_FileInformation = XIP_ReadFileTable(XIP, XIP_DataStart, XIP_FileCount)
            XIP_FileNames = XIP_ReadFileNameTable(XIP, XIP_FileNameCount)
            
            XIP_SaveFiles(XIP, XIP_FileInformation, XIP_FileNames, outPath)

    elif magic == b'XPR0': #Original Xbox XPR0 image/texture format
        output = fileTools.folder(file)+"/"+fileTools.nameNoExt(file)+".tga"
        
        with open(file, "rb") as XBX:
            XBX_ImageDataStartOffset, XBX_ImageDataLength, XBX_CompressionType, XBX_XSize, XBX_YSize = XBX_ReadHeader(XBX)
            XBX_ConvertedPixelData = XBX_ConvertImage(XBX, XBX_ImageDataStartOffset, XBX_ImageDataLength, XBX_CompressionType, XBX_XSize, XBX_YSize)

            XBX_SaveImage(XBX_ConvertedPixelData, XBX_XSize, XBX_YSize, output)
            
    else:
        print(magic)
        
