from libraries.codingTools import *

def SARC_GetHash(name, key): #Python port of Nintendo's SARC filename hash function
    result = 0 #The result gets stored here

    for characterIndex in range(len(name)):
        result = (ord(name[characterIndex]) + result * key) & 0xFFFFFFFF

    return result

def SARC_GetZeroTerminatedStringAndAlign(reader):
    data = b'' #The final, stored data
    value = b'' #What's being read
    
    while value != b'\x00':
        value = reader.read(1)
        data+=value

    offset = reader.tell() #Get current offset following the string's end
    aligned = (offset + 3) & ~0x03 #Align the offset
    
    reader.seek(aligned) #Seek to the aligned offset

    return (data.rstrip(b'\x00')).decode('UTF-8') #Yay! We got the string!
    
def SARC_ReadHeader(SARC): #A function that gets the values in a SARC header (and sets the endianness)
    if SARC.read(4) == b'SARC':
        SARC_HeaderLength = SARC.read(2)
        SARC_ByteOrder = SARC.read(2)
        
        if SARC_ByteOrder == b'\xFE\xFF': #Big
            SARC_ValueDecoder = BE_Unpack
        elif SARC_ByteOrder == b'\xFF\xFE': #Little
            SARC_ValueDecoder = LE_Unpack
            
        SARC_FileSize = SARC_ValueDecoder.uint(SARC.read(4))
        SARC_DataStartOffset = SARC_ValueDecoder.uint(SARC.read(4))
        SARC_VersionNumber = SARC_ValueDecoder.ushort(SARC.read(2))
        SARC_Reserved = SARC.read(2)
        
    return SARC_ValueDecoder, SARC_DataStartOffset

def SARC_FileAllocationTable(SARC, SARC_ValueDecoder):
    entries = []
    SARC_SFATMagic = SARC.read(4) #magic can be skipped
    SARC_SFATHeaderLength = SARC.read(2) #Length can be skipped, always 0xC
    SARC_SFATNodeCount = SARC_ValueDecoder.ushort(SARC.read(2))
    SARC_SFATFileNameHashKey = SARC_ValueDecoder.uint(SARC.read(4))
    
    for node in range(SARC_SFATNodeCount):
        SARC_FileNameHash = SARC_ValueDecoder.uint(SARC.read(4))
        SARC_FileAttributes = SARC_ValueDecoder.uint(SARC.read(4))
        SARC_BeginningOfNodeFileData = SARC_ValueDecoder.uint(SARC.read(4))
        SARC_EndOfNodeFileData = SARC_ValueDecoder.uint(SARC.read(4))
        entries.append([SARC_FileNameHash, SARC_FileAttributes, SARC_BeginningOfNodeFileData, SARC_EndOfNodeFileData])

    return entries, SARC_SFATFileNameHashKey

def SARC_FileNameTable(SARC, entryCount):
    SARC_SFNTMagic = SARC.read(4) #magic can be skipped
    SARC_SFNTHeaderLength = SARC.read(2) #Length can be skipped, always 0x8
    SARC.seek(2, 1) #Skip reserved bytes

    SARC_FileNames = [] #This is where all of the interesting filenames go

    for stringIndex in range(entryCount):
        SARC_FileName = SARC_GetZeroTerminatedStringAndAlign(SARC)
        SARC_FileNames.append(SARC_FileName)
        
    return SARC_FileNames

def SARC_SaveFiles(SARC, SARC_Nodes, SARC_FileNames, SARC_FileNameHashKey, SARC_DataStartOffset, outPath):
    for SARC_Node in SARC_Nodes: #Time to extract!
        SARC_NameHash        = SARC_Node[0]
        SARC_FileAttributes  = SARC_Node[1] #I should probably make use of this
        SARC_StartOfFileData = SARC_Node[2]
        SARC_EndOfFileData   = SARC_Node[3]
        
        SARC_FileLength      = SARC_EndOfFileData - SARC_StartOfFileData
        
        for SARC_FileName in SARC_FileNames:
            SARC_Hash = SARC_GetHash(SARC_FileName, SARC_FileNameHashKey)
            if SARC_Hash == SARC_NameHash:
                break

        SARC.seek(SARC_StartOfFileData+SARC_DataStartOffset)

        SARC_FileData = SARC.read(SARC_FileLength)

        with open(outPath+SARC_FileName, "w+b") as output:
            output.write(SARC_FileData)
