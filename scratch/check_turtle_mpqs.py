import ctypes
from ctypes import c_void_p, c_char_p, c_wchar_p, c_ulong, byref
import glob

stormlib_path = r"C:\Program Files\OctoLauncher\resources\app.asar.unpacked\node_modules\stormlib-node\dist\StormLib.dll"
stormlib = ctypes.WinDLL(stormlib_path)

SFileOpenArchive = stormlib.SFileOpenArchive
SFileOpenArchive.argtypes = [c_wchar_p, c_ulong, c_ulong, ctypes.POINTER(c_void_p)]
SFileOpenArchive.restype = ctypes.c_bool

SFileOpenFileEx = stormlib.SFileOpenFileEx
SFileOpenFileEx.argtypes = [c_void_p, c_char_p, c_ulong, ctypes.POINTER(c_void_p)]
SFileOpenFileEx.restype = ctypes.c_bool

SFileCloseFile = stormlib.SFileCloseFile
SFileCloseFile.argtypes = [c_void_p]

SFileCloseArchive = stormlib.SFileCloseArchive
SFileCloseArchive.argtypes = [c_void_p]

candidate_files = [
    b"DBFilesClient\\Item.dbc",
    b"DBFilesClient\\ItemSet.dbc",
    b"DBFilesClient\\Spell.dbc"
]

for mpq_path in glob.glob(r"C:\TurtleWoW\Data\*.mpq") + glob.glob(r"C:\TurtleWoW\Data\*.MPQ"):
    h_archive = c_void_p()
    if SFileOpenArchive(mpq_path, 0, 0x00000100, byref(h_archive)):
        found = []
        for cf in candidate_files:
            h_file = c_void_p()
            if SFileOpenFileEx(h_archive, cf, 0, byref(h_file)):
                found.append(cf.decode('ascii'))
                SFileCloseFile(h_file)
        if found:
            print(f"{mpq_path}: {found}")
        SFileCloseArchive(h_archive)
