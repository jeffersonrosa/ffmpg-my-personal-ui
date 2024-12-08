import os

def list_media_files(media_folder, extensions):
    if not os.path.isdir(media_folder):
        return []
    files = []
    for f in os.listdir(media_folder):
        full_path = os.path.join(media_folder, f)
        if os.path.isfile(full_path) and any(f.lower().endswith(ext) for ext in extensions):
            files.append(full_path)
    return files

def choose_from_list(items, prompt="Selecione uma opção: "):
    for i, item in enumerate(items, start=1):
        print(f"{i} - {item}")
    choice = input(prompt)
    try:
        idx = int(choice)-1
        if 0 <= idx < len(items):
            return items[idx]
    except:
        pass
    return None
