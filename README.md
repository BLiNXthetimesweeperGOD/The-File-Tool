# The-File-Tool
Great name, I know. 

This is a tool that unpacks and converts several file formats I've encountered in the past. 

The end goal is to have each format split up into easy to read functions. 


Feel free to reimplement any part of this code so long as you credit either me or the people/resources listed below.

## Supported formats
- HOG (Bubsy 3D)
- HOT (Voodoo Vince Remastered)
- MIT (BLiNX: the Time Sweeper)
- RAX (Children of Mana)
- SARC (Nintendo)
- XBX (Microsoft Xbox)
- XIP (Microsoft Xbox)

## Planned (but not yet implemented) formats
- NARC (Nintendo DS)
- XSSB (BLiNX: the Time Sweeper)

## Credits
Huge thanks to PatrickHamster (Bartłomiej Duda) for letting me use their Xbox swizzle code! The original can be found here:

https://github.com/bartlomiejduda/ReverseBox/blob/main/reversebox/image/swizzling/swizzle_morton.py


The Original Xbox XIP unpacker is based on this program by MaTiAz and JayFoxRox:

https://github.com/JayFoxRox/UnXiP


The Nintendo SARC/SZS unpacker was made using this documentation:

https://mk8.tockdom.com/wiki/SARC_(File_Format)

https://wiki.tockdom.com/wiki/Yaz0_(File_Format)


## Usage instructions
Using this is as easy as running "File Tool.py" and selecting a file.

Files will be output in a folder named after the input file. 

Files are not saved relative to the folder containing the script itself.



Examples to help explain a bit better:

"R:/Test folder/XBAHKS.xip" will unpack to "R:/Test folder/XBAHKS/"

If the script is in "R:/Weird Snake Programs/", the files will still go in "R:/Test folder/XBAHKS/"
