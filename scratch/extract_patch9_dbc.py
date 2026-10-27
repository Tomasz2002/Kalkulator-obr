import ctypes
from ctypes import c_void_p, c_char_p, c_wchar_p, c_ulong, byref
import struct

stormlib_path = r"C:\Program Files\OctoLauncher\resources\app.asar.unpacked\node_modules\stormlib-node\dist\StormLib.dll"
stormlib = ctypes.WinDLL(stormlib_path)

SFileOpenArchive = stormlib.SFileOpenArchive
SFileOpenArchive.argtypes = [c_wchar_p, c_ulong, c_ulong, ctypes.POINTER(c_void_p)]
SFileOpenArchive.restype = ctypes.c_bool

SFileOpenFileEx = stormlib.SFileOpenFileEx
SFileOpenFileEx.argtypes = [c_void_p, c_char_p, c_ulong, ctypes.POINTER(c_void_p)]
SFileOpenFileEx.restype = ctypes.c_bool

SFileReadFile = stormlib.SFileReadFile
SFileReadFile.argtypes = [c_void_p, c_void_p, c_ulong, ctypes.POINTER(c_ulong), c_void_p]
SFileReadFile.restype = ctypes.c_bool

SFileGetFileSize = stormlib.SFileGetFileSize
SFileGetFileSize.argtypes = [c_void_p, ctypes.POINTER(c_ulong)]
SFileGetFileSize.restype = c_ulong

SFileCloseFile = stormlib.SFileCloseFile
SFileCloseArchive = stormlib.SFileCloseArchive

mpq_path = r"C:\TurtleWoW\Data\patch-9.mpq"
h_archive = c_void_p()
if SFileOpenArchive(mpq_path, 0, 0x00000100, byref(h_archive)):
    h_file = c_void_p()
    if SFileOpenFileEx(h_archive, b"DBFilesClient\\ItemSet.dbc", 0, byref(h_file)):
        size = SFileGetFileSize(h_file, None)
        buf = ctypes.create_string_buffer(size)
        read = c_ulong()
        SFileReadFile(h_file, buf, size, byref(read), None)
        data = buf.raw[:read.value]
        with open('data/extracted_client_dbc/patch-9.mpq_ItemSet.dbc', 'wb') as f:
            f.write(data)
        print(f"Extracted patch-9.mpq ItemSet.dbc: {len(data)} bytes")
        SFileCloseFile(h_file)
    SFileCloseArchive(h_archive)
