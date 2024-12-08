from ffmpeg_installer import ensure_ffmpeg
from menu import show_main_menu
from config_manager import load_config, ensure_media_folder, ensure_export_folder

def main():
    ensure_ffmpeg()
    cfg = load_config()
    ensure_media_folder(cfg)
    ensure_export_folder(cfg)
    show_main_menu(cfg)

if __name__ == "__main__":
    main()
