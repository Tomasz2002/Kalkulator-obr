import ctypes, os

dll = ctypes.WinDLL(r'C:\Program Files\OctoLauncher\resources\app.asar.unpacked\node_modules\stormlib-node\dist\StormLib.dll')
dll.SFileOpenArchive.argtypes = [ctypes.c_wchar_p, ctypes.c_uint32, ctypes.c_uint32, ctypes.POINTER(ctypes.c_void_p)]
dll.SFileOpenArchive.restype = ctypes.c_bool
dll.SFileFindFirstFile.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_void_p, ctypes.c_char_p]
dll.SFileFindFirstFile.restype = ctypes.c_void_p
dll.SFileFindNextFile.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
dll.SFileFindNextFile.restype = ctypes.c_bool
dll.SFileFindClose.argtypes = [ctypes.c_void_p]
dll.SFileFindClose.restype = ctypes.c_bool
dll.SFileCloseArchive.argtypes = [ctypes.c_void_p]
dll.SFileCloseArchive.restype = ctypes.c_bool

# SFILE_FIND_DATA structure:
# char   cFileName[MAX_PATH];
# char * szPlainName;
# DWORD  dwFileHash;
# DWORD  dwFileHashA;
# DWORD  dwFileHashB;
# LCID   lcLocale;
# DWORD  dwPlatform;
# DWORD  dwFileSize;
# DWORD  dwCompSize;
# DWORD  dwVersion;
# DWORD  dwFlags;

class SFILE_FIND_DATA(ctypes.Structure):
    _fields_ = [
        ("cFileName", ctypes.c_char * 260),
        ("szPlainName", ctypes.c_char_p),
        ("dwFileHash", ctypes.c_uint32),
        ("dwFileHashA", ctypes.c_uint32),
        ("dwFileHashB", ctypes.c_uint32),
        ("lcLocale", ctypes.c_uint32),
        ("dwPlatform", ctypes.c_uint32),
        ("dwFileSize", ctypes.c_uint32),
        ("dwCompSize", ctypes.c_uint32),
        ("dwVersion", ctypes.c_uint32),
        ("dwFlags", ctypes.c_uint32),
    ]

for fname in ['patch-5.mpq', 'patch-4.mpq', 'patch-3.mpq']:
    p = os.path.join(r'C:\Octo wow gowno\Data', fname)
    if not os.path.exists(p): continue
    hMpq = ctypes.c_void_p()
    if dll.SFileOpenArchive(p, 0, 0, ctypes.byref(hMpq)):
        fd = SFILE_FIND_DATA()
        hFind = dll.SFileFindFirstFile(hMpq, b'*item*.dbc', ctypes.byref(fd), None)
        print(f'=== {fname} ===')
        if hFind:
            while True:
                print(' ', fd.cFileName.decode('utf-8', errors='ignore'), f'({fd.dwFileSize} bytes)')
                if not dll.SFileFindNextFile(hFind, ctypes.byref(fd)):
                    break
            dll.SFileFindClose(hFind)
        dll.SFileCloseArchive(hMpq)
