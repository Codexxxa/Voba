import zipfile
import json
import re

def is_dialog_string(line):
    if not isinstance(line, str): return False
    s = line.strip()
    # Ada huruf, bukan tag kode doang, panjang > 1
    return bool(re.search(r'[a-zA-Z]', s)) and len(s) > 1

# Key umum yang bisa berisi dialog di RPGM berbagai versi/plugin
dialog_keys = {"text", "message", "desc", "name", "lines"}

# Event code yang biasanya berisi dialog
dialog_codes = {101, 102, 401, 102, 405}

def scan_zip_for_dialogs(zip_path):
    with zipfile.ZipFile(zip_path, 'r') as zipf:
        dialog_files = []
        for fname in zipf.namelist():
            if not fname.lower().endswith('.json'):
                continue
            try:
                content = zipf.read(fname).decode('utf-8')
                data = json.loads(content)
                found = False
                def recursive_check(obj):
                    nonlocal found
                    if found: return  # Sudah ketemu dialog, tidak perlu cek lebih jauh
                    # Cek pola key dialog langsung
                    if isinstance(obj, dict):
                        for k, v in obj.items():
                            # 1. Jika key dialog klasik (text, message, dsb)
                            if k.lower() in dialog_keys:
                                if isinstance(v, list):
                                    if any(is_dialog_string(str(s)) for s in v):
                                        found = True
                                        return
                                elif isinstance(v, str):
                                    if is_dialog_string(v):
                                        found = True
                                        return
                            # 2. Jika pola RPGMV/MZ: commandList + code + parameters
                            if k == "code" and "parameters" in obj:
                                if obj["code"] in dialog_codes:
                                    params = obj["parameters"]
                                    if isinstance(params, list) and any(is_dialog_string(str(p)) for p in params):
                                        found = True
                                        return
                        for v in obj.values():
                            recursive_check(v)
                    elif isinstance(obj, list):
                        for item in obj:
                            recursive_check(item)
                recursive_check(data)
                if found:
                    dialog_files.append(fname)
            except Exception:
                continue
        return dialog_files

# --- Ganti path sesuai lokasi ZIP-mu
zipname = "/storage/emulated/0/Download/Game.zip"

if __name__ == "__main__":
    hasil = scan_zip_for_dialogs(zipname)
    print("File yang mengandung dialog RPGM:")
    for f in hasil:
        print(f)