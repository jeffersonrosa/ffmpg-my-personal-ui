import subprocess
import os
from conversions import build_ffmpeg_command
from utils import list_media_files, choose_from_list
from ffmpeg_installer import get_ffmpeg_command
from config_manager import save_config

def show_main_menu(cfg):
    while True:
        media_folder = cfg["media_folder"]
        export_folder = cfg.get("export_folder", media_folder)
        print("==== MENU PRINCIPAL ====")
        print("Pasta atual de mídia:", media_folder)
        print("Pasta atual de exportação:", export_folder)
        print("[1] Conversão Individual")
        print("[2] Conversão em Lote")
        print("[3] Alterar pasta de mídia")
        print("[4] Alterar pasta de exportação")
        print("[0] Sair")
        op = input("Opção: ")
        if op == "1":
            conversion_individual(cfg)
        elif op == "2":
            conversion_batch(cfg)
        elif op == "3":
            change_media_folder(cfg)
        elif op == "4":
            change_export_folder(cfg)
        elif op == "0":
            break
        else:
            print("Opção inválida.")

def change_media_folder(cfg):
    print("Caminho atual de mídia:", cfg["media_folder"])
    folder = input("Digite o novo caminho da pasta de mídia: ").strip()
    if folder:
        if not os.path.isdir(folder):
            print("A pasta não existe. Tentando criar...")
            try:
                os.makedirs(folder, exist_ok=True)
                print("Pasta criada:", folder)
            except Exception as e:
                print("Erro ao criar a pasta:", e)
                print("Pasta não alterada.")
                return
        cfg["media_folder"] = folder
        # Se a export_folder estiver vazia, usar a mesma da mídia
        if not cfg.get("export_folder"):
            cfg["export_folder"] = folder
        save_config(cfg)
        print("Pasta de mídia alterada com sucesso!")
    else:
        print("Nenhuma pasta informada. Pasta não alterada.")

def change_export_folder(cfg):
    print("Caminho atual de exportação:", cfg.get("export_folder", cfg["media_folder"]))
    folder = input("Digite o novo caminho da pasta de exportação: ").strip()
    if folder:
        if not os.path.isdir(folder):
            print("A pasta não existe. Tentando criar...")
            try:
                os.makedirs(folder, exist_ok=True)
                print("Pasta criada:", folder)
            except Exception as e:
                print("Erro ao criar a pasta:", e)
                print("Pasta não alterada.")
                return
        cfg["export_folder"] = folder
        save_config(cfg)
        print("Pasta de exportação alterada com sucesso!")
    else:
        print("Nenhuma pasta informada. Pasta não alterada.")

def get_fps_choice():
    print("Escolha FPS: ")
    fps_opts = ["original", "30", "24", "18", "12"]
    fps = choose_from_list(fps_opts, "FPS: ")
    return fps

def get_resolution_choice():
    print("Escolha resolução: ")
    res_opts = ["original", "fullhd", "hd", "whatsapp"]
    res = choose_from_list(res_opts, "Resolução: ")
    return res

def get_audio_choice():
    print("Escolha formato de áudio: ")
    audio_opts = ["manter (copy)", "ogg", "mp3", "m4a"]
    choice = choose_from_list(audio_opts, "Áudio: ")
    if choice and "manter" in choice:
        return None
    return choice

def get_audio_bitrate_choice():
    print("Escolha bitrate de áudio: ")
    br_opts = ["nenhum (copy)", "128k", "96k"]
    choice = choose_from_list(br_opts, "Bitrate: ")
    if choice and "nenhum" in choice:
        return None
    return choice

def ask_audio_only():
    ans = input("Somente áudio? (s/n): ")
    return ans.lower().startswith('s')

def ask_video_only():
    ans = input("Somente vídeo? (s/n): ")
    return ans.lower().startswith('s')

def conversion_individual(cfg):
    media_folder = cfg["media_folder"]
    export_folder = cfg.get("export_folder", media_folder)
    exts = cfg.get("media_extensions", {})
    all_exts = exts.get("audio",[]) + exts.get("video",[])
    files = list_media_files(media_folder, all_exts)
    if not files:
        print("Nenhum arquivo de mídia encontrado.")
        return
    # Mostrar apenas o nome do arquivo sem o path no menu
    display_files = [os.path.basename(f) for f in files]
    chosen = choose_from_list(display_files, "Escolha o arquivo: ")
    if not chosen:
        print("Opção inválida.")
        return
    # Recuperar caminho completo
    input_file = os.path.join(media_folder, chosen)

    fps = get_fps_choice()
    resolution = get_resolution_choice()
    audio_format = get_audio_choice()
    audio_bitrate = get_audio_bitrate_choice()
    audio_only = ask_audio_only()
    video_only = False
    if not audio_only:
        video_only = ask_video_only()

    output_file = input("Nome do arquivo de saída (ex: output.mp4): ").strip()
    if not output_file:
        output_file = "output.mp4"
    output_file = os.path.join(export_folder, output_file)

    cmd_args = build_ffmpeg_command(
        input_file=input_file,
        output_file=output_file,
        fps=fps,
        resolution=resolution,
        audio_format=audio_format,
        audio_bitrate=audio_bitrate,
        video_only=video_only,
        audio_only=audio_only
    )
    ffmpeg_cmd = [get_ffmpeg_command()] + cmd_args
    print("Executando:", " ".join(ffmpeg_cmd))
    subprocess.run(ffmpeg_cmd)
    print("Conversão concluída.")

def conversion_batch(cfg):
    media_folder = cfg["media_folder"]
    export_folder = cfg.get("export_folder", media_folder)
    exts = cfg.get("media_extensions", {})
    all_exts = exts.get("audio",[]) + exts.get("video",[])
    files = list_media_files(media_folder, all_exts)
    if not files:
        print("Nenhum arquivo de mídia encontrado.")
        return

    fps = get_fps_choice()
    resolution = get_resolution_choice()
    audio_format = get_audio_choice()
    audio_bitrate = get_audio_bitrate_choice()
    audio_only = ask_audio_only()
    video_only = False
    if not audio_only:
        video_only = ask_video_only()

    if not os.path.exists(export_folder):
        os.makedirs(export_folder, exist_ok=True)

    for f in files:
        base, ext = os.path.splitext(os.path.basename(f))
        output_file = os.path.join(export_folder, base + "_conv.mp4")
        cmd_args = build_ffmpeg_command(
            input_file=f,
            output_file=output_file,
            fps=fps,
            resolution=resolution,
            audio_format=audio_format,
            audio_bitrate=audio_bitrate,
            video_only=video_only,
            audio_only=audio_only
        )
        ffmpeg_cmd = [get_ffmpeg_command()] + cmd_args
        print("Executando:", " ".join(ffmpeg_cmd))
        subprocess.run(ffmpeg_cmd)
    print("Conversão em lote concluída.")
