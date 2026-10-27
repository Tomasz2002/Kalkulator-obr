import ctypes, os

dll = ctypes.WinDLL(r'C:\Program Files\OctoLauncher\resources\app.asar.unpacked\node_modules\stormlib-node\dist\StormLib.dll')

dll.SFileOpenArchive.argtypes = [ctypes.c_wchar_p, ctypes.c_uint32, ctypes.c_uint32, ctypes.POINTER(ctypes.c_void_p)]
dll.SFileOpenArchive.restype = ctypes.c_bool

dll.SFileExtractFile.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_wchar_p, ctypes.c_uint32]
dll.SFileExtractFile.restype = ctypes.c_bool

dll.SFileCloseArchive.argtypes = [ctypes.c_void_p]
dll.SFileCloseArchive.restype = ctypes.c_bool

os.makedirs('data/extracted_client_dbc', exist_ok=True)

for fname in ['patch-5.mpq', 'patch-4.mpq', 'patch-O.mpq', 'patch-3.mpq', 'patch-2.mpq', 'patch-1.mpq', 'patch.MPQ', 'dbc.MPQ']:
    mpq_path = os.path.join(r'C:\Octo wow gowno\Data', fname)
    if not os.path.exists(mpq_path): continue
    hMpq = ctypes.c_void_p()
    res = dll.SFileOpenArchive(mpq_path, 0, 0, ctypes.byref(hMpq))
    if not res:
        err = ctypes.GetLastError()
        print(f'{fname}: failed to open archive (error {err})')
        continue
    print(f'{fname}: successfully opened!')
    
    for dbc in ['DBFilesClient\\ItemSet.dbc', 'DBFilesClient\\Spell.dbc']:
        out_name = f"{fname}_{os.path.basename(dbc)}"
        out_path = os.path.abspath(os.path.join('data/extracted_client_dbc', out_name))
        ok = dll.SFileExtractFile(hMpq, dbc.encode('utf-8'), out_path, 0)
        if ok:
            print(f'  Extracted {dbc} -> {out_name} ({os.path.getsize(out_path)} bytes)')
        else:
            err = ctypes.GetLastError()
            if err != 2:
                print(f'  Failed to extract {dbc}: error {err}')
    
    dll.SFileCloseArchive(hMpq)
