import os
import json

CONFIG_FILE = "config.json"

def get_default_videos_path():
    userprofile = os.environ.get("USERPROFILE", "")
    if userprofile:
        return os.path.join(userprofile, "Videos")
    return os.getcwd()  # fallback se não achar USERPROFILE

def load_config():
    if not os.path.exists(CONFIG_FILE):
        # Cria config padrão
        default_config = {
            "media_extensions": {
                "audio": [".ogg", ".mp3", ".m4a"],
                "video": [".mp4", ".mkv"]
            },
            "media_folder": get_default_videos_path(),
            "export_folder": ""  # vazio por padrão, usará a pasta de mídia se vazio
        }
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(default_config, f, indent=4)
        return default_config
    else:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            cfg = json.load(f)
            return cfg

def save_config(cfg):
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(cfg, f, indent=4)

def ensure_media_folder(cfg):
    media_folder = cfg.get("media_folder", "")
    if not media_folder or not os.path.isdir(media_folder):
        print("A pasta de mídia não está configurada ou não existe.")
        folder = input("Digite o caminho da pasta de mídia (Enter para usar a pasta de Vídeos do usuário): ").strip()
        if not folder:
            folder = get_default_videos_path()
        if not os.path.isdir(folder):
            print("A pasta não existe. Tentando criar...")
            try:
                os.makedirs(folder, exist_ok=True)
                print("Pasta criada:", folder)
            except Exception as e:
                print("Erro ao criar a pasta:", e)
                print("Usando pasta atual.")
                folder = os.getcwd()
        cfg["media_folder"] = folder
        # Se a export_folder estiver vazia, ela ficará igual a media_folder
        if not cfg.get("export_folder"):
            cfg["export_folder"] = folder
        save_config(cfg)
    return cfg["media_folder"]

def ensure_export_folder(cfg):
    # Se export_folder não estiver configurada ou vazia, usar a media_folder
    export_folder = cfg.get("export_folder", "")
    if not export_folder:
        export_folder = cfg["media_folder"]
        cfg["export_folder"] = export_folder
        save_config(cfg)

    if not os.path.isdir(export_folder):
        print("A pasta de exportação não existe. Tentando criar...")
        try:
            os.makedirs(export_folder, exist_ok=True)
            print("Pasta criada:", export_folder)
        except Exception as e:
            print("Erro ao criar a pasta de exportação:", e)
            # se não conseguir criar, fallback na media_folder
            export_folder = cfg["media_folder"]
            cfg["export_folder"] = export_folder
            print("Usando pasta de mídia como exportação:", export_folder)
            save_config(cfg)

    return cfg["export_folder"]

def get_all_extensions(cfg):
    audio_exts = cfg.get("media_extensions", {}).get("audio", [])
    video_exts = cfg.get("media_extensions", {}).get("video", [])
    return audio_exts + video_exts
