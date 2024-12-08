import subprocess
import os
import math
import json
import questionary
from conversions import build_ffmpeg_command
from utils import list_media_files
from ffmpeg_installer import get_ffmpeg_command
from config_manager import save_config

def get_video_metadata(input_file):
    ffprobe_cmd = [
        "ffprobe",
        "-v", "error",
        "-select_streams", "v:0",
        "-show_entries", "stream=r_frame_rate,width,height",
        "-of", "json",
        input_file
    ]
    fps = None
    width = None
    height = None
    try:
        result = subprocess.run(ffprobe_cmd, capture_output=True, text=True)
        data = json.loads(result.stdout)
        streams = data.get("streams", [])
        if streams:
            stream = streams[0]
            fps_str = stream.get("r_frame_rate", "0/0")
            w = stream.get("width")
            h = stream.get("height")
            num, den = fps_str.split('/')
            if int(den) != 0:
                fps = int(num)/int(den)
            width = w
            height = h
    except:
        pass

    # Tentar obter bitrate de áudio
    audio_bitrate = None
    ffprobe_cmd_audio = [
        "ffprobe",
        "-v", "error",
        "-select_streams", "a:0",
        "-show_entries", "stream=bit_rate",
        "-of", "json",
        input_file
    ]
    try:
        result_a = subprocess.run(ffprobe_cmd_audio, capture_output=True, text=True)
        data_a = json.loads(result_a.stdout)
        streams_a = data_a.get("streams", [])
        if streams_a:
            a_stream = streams_a[0]
            if "bit_rate" in a_stream and a_stream["bit_rate"]:
                # bit_rate vem em bits/s, converter para kbps
                bps = int(a_stream["bit_rate"])
                kbps = bps // 1000
                audio_bitrate = kbps
    except:
        pass

    return {"fps": fps, "width": width, "height": height, "audio_bitrate": audio_bitrate}

def numeric_or_arrow_choice(question, choices):
    """
    Exibe primeiro as opções com números. Se o usuário digitar um número válido, retorna a escolha.
    Caso contrário, usa o questionary.select com setas.
    """
    print(question)
    for i, c in enumerate(choices):
        print(f" [{i}] {c}")

    ans = input("Digite o número da opção ou pressione Enter para usar setas: ").strip()
    if ans.isdigit():
        idx = int(ans)
        if 0 <= idx < len(choices):
            return choices[idx]

    # fallback para setas
    return questionary.select(question, choices=choices, instruction="Use as setas do teclado ou digite o número:").ask()

def show_main_menu(cfg):
    while True:
        media_folder = cfg["media_folder"]
        export_folder = cfg.get("export_folder", media_folder)
        choices = [
            "Conversão Individual",
            "Conversão em Lote",
            "Alterar pasta de mídia",
            "Alterar pasta de exportação",
            "Sair"
        ]
        choice = numeric_or_arrow_choice(
            f"==== MENU PRINCIPAL ====\nPasta atual de mídia: {media_folder}\nPasta atual de exportação: {export_folder}",
            choices
        )
        if choice == "Conversão Individual":
            conversion_individual(cfg)
        elif choice == "Conversão em Lote":
            conversion_batch(cfg)
        elif choice == "Alterar pasta de mídia":
            change_media_folder(cfg)
        elif choice == "Alterar pasta de exportação":
            change_export_folder(cfg)
        elif choice == "Sair" or choice is None:
            break

def change_media_folder(cfg):
    current = cfg["media_folder"]
    folder = questionary.text(f"Caminho atual de mídia: {current}\nDigite o novo caminho da pasta de mídia (Enter para cancelar):").ask()
    if folder and folder.strip():
        folder = folder.strip()
        if not os.path.isdir(folder):
            create = questionary.confirm("A pasta não existe. Criar?").ask()
            if create:
                try:
                    os.makedirs(folder, exist_ok=True)
                    print("Pasta criada:", folder)
                except Exception as e:
                    print("Erro ao criar a pasta:", e)
                    print("Pasta não alterada.")
                    return
            else:
                return
        cfg["media_folder"] = folder
        if not cfg.get("export_folder"):
            cfg["export_folder"] = folder
        save_config(cfg)
        print("Pasta de mídia alterada com sucesso!")

def change_export_folder(cfg):
    current = cfg.get("export_folder", cfg["media_folder"])
    folder = questionary.text(f"Caminho atual de exportação: {current}\nDigite o novo caminho da pasta de exportação (Enter para cancelar):").ask()
    if folder and folder.strip():
        folder = folder.strip()
        if not os.path.isdir(folder):
            create = questionary.confirm("A pasta não existe. Criar?").ask()
            if create:
                try:
                    os.makedirs(folder, exist_ok=True)
                    print("Pasta criada:", folder)
                except Exception as e:
                    print("Erro ao criar a pasta de exportação:", e)
                    print("Pasta não alterada.")
                    return
            else:
                return
        cfg["export_folder"] = folder
        save_config(cfg)
        print("Pasta de exportação alterada com sucesso!")

def conversion_individual(cfg):
    media_folder = cfg["media_folder"]
    export_folder = cfg.get("export_folder", media_folder)
    exts = cfg.get("media_extensions", {})
    all_exts = exts.get("audio",[]) + exts.get("video",[])
    files = list_media_files(media_folder, all_exts)
    if not files:
        print("Nenhum arquivo de mídia encontrado.")
        return

    chosen_file = None
    if len(files) == 1:
        base = os.path.basename(files[0])
        c = numeric_or_arrow_choice(
            f"Encontrado apenas 1 arquivo: {base}\nDeseja prosseguir com esse arquivo?",
            ["Sim", "Não (voltar)"]
        )
        if c == "Sim":
            chosen_file = files[0]
        else:
            return
    else:
        display_files = [os.path.basename(f) for f in files]
        display_files.append("Voltar")
        c = numeric_or_arrow_choice("Escolha o arquivo:", display_files)
        if c == "Voltar" or c is None:
            return
        chosen_file = os.path.join(media_folder, c)

    meta = get_video_metadata(chosen_file)

    # Vídeo ou Áudio?
    c = numeric_or_arrow_choice("Deseja converter para Vídeo ou Áudio?", ["Vídeo", "Áudio", "Voltar"])
    if c == "Voltar" or c is None:
        return
    conv_type = c

    if conv_type == "Vídeo":
        # FPS
        fps_choice = choose_fps(meta)
        if fps_choice is None:
            return
        # Resolução
        resolution_choice = choose_resolution(meta)
        if resolution_choice is None:
            return
        # Áudio no vídeo
        audio_format, audio_bitrate = choose_video_audio_options(meta)
        if audio_format == "Voltar":
            return
        audio_only = False
        video_only = False
        summary = f"Arquivo: {chosen_file}\nConversão: Vídeo\nFPS: {fps_choice}\nResolução: {resolution_choice}\nÁudio: {audio_format or 'copy'}\nBitrate áudio: {audio_bitrate or 'padrão'}\nExportar para: {export_folder}"
    else:
        # Áudio
        audio_format = choose_audio_format_for_audio_only()
        if audio_format == "Voltar" or audio_format is None:
            return
        audio_bitrate = choose_audio_bitrate(meta, audio_only_mode=True)
        if audio_bitrate == "Voltar":
            return
        audio_only = True
        video_only = False
        fps_choice = "original"
        resolution_choice = "original"
        summary = f"Arquivo: {chosen_file}\nConversão: Áudio\nFormato: {audio_format}\nBitrate: {audio_bitrate or 'padrão'}\nExportar para: {export_folder}"

    # Nome do arquivo de saída
    default_name = "output"
    prompt_out = f"Nome do arquivo de saída (será salvo em {export_folder}, Enter para '{default_name}'):"
    output_file = questionary.text(prompt_out).ask()
    if not output_file:
        output_file = default_name

    if conv_type == "Áudio":
        ext_map = {"ogg": ".ogg", "mp3": ".mp3", "m4a": ".m4a"}
        output_ext = ext_map.get(audio_format, ".ogg")
    else:
        output_ext = ".mp4"

    output_file = output_file + output_ext
    output_file = os.path.join(export_folder, output_file)

    proceed = numeric_or_arrow_choice(
        f"Confirme a conversão:\n{summary}\nSaída: {output_file}\nProsseguir?",
        ["Sim", "Voltar", "Cancelar"]
    )
    if proceed == "Voltar":
        return
    if proceed == "Cancelar" or proceed is None:
        return

    if conv_type == "Áudio":
        cmd_args = build_ffmpeg_command(
            input_file=chosen_file,
            output_file=output_file,
            fps=fps_choice if fps_choice != "original" else None,
            resolution=resolution_choice if resolution_choice != "original" else None,
            audio_format=audio_format,
            audio_bitrate=audio_bitrate,
            video_only=False,
            audio_only=True
        )
    else:
        cmd_args = build_ffmpeg_command(
            input_file=chosen_file,
            output_file=output_file,
            fps=fps_choice if fps_choice != "original" else None,
            resolution=resolution_choice if resolution_choice != "original" else None,
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
    print("Conversão em lote não foi modificada neste exemplo.")
    return

def choose_fps(meta):
    fps_original = meta["fps"]
    if fps_original is None or fps_original <= 0:
        fps_original = 30
    fps_str = f"original ({round(fps_original, 2)} fps)"
    choices = [
        fps_str,
        "30",
        "24",
        "18",
        "12",
        "Custom (1 até {} fps)".format(int(fps_original)),
        "Voltar"
    ]
    c = numeric_or_arrow_choice("Escolha FPS:", choices)
    if c == "Voltar" or c is None:
        return None
    if c == fps_str:
        return "original"
    if c.startswith("Custom"):
        custom_val = questionary.text(f"Digite o FPS desejado (1-{int(fps_original)}):").ask()
        if not (custom_val and custom_val.isdigit()):
            return None
        val = int(custom_val)
        if val < 1 or val > int(fps_original):
            return None
        return str(val)
    return c

def choose_resolution(meta):
    w = meta["width"]
    h = meta["height"]
    if w is None or h is None:
        w,h = 1920,1080
    original_str = f"original ({w}x{h})"
    choices = [
        original_str,
        "fullhd (1920x1080)",
        "hd (1280x720)",
        "whatsapp (854x480)",
        "Outras porcentagens",
        "Voltar"
    ]
    c = numeric_or_arrow_choice("Escolha resolução:", choices)
    if c == "Voltar" or c is None:
        return None
    if c == original_str:
        return "original"
    if c.startswith("fullhd"):
        return "fullhd"
    if c.startswith("hd"):
        return "hd"
    if c.startswith("whatsapp"):
        return "whatsapp"
    if c.startswith("Outras porcentagens"):
        percent_choices = []
        for p in range(90, 0, -10):
            new_w = math.floor(w*(p/100.0))
            new_h = math.floor(h*(p/100.0))
            percent_choices.append(f"{p}% ({new_w}x{new_h})")
        percent_choices.append("Voltar")
        c2 = numeric_or_arrow_choice("Escolha a porcentagem:", percent_choices)
        if c2 == "Voltar" or c2 is None:
            return choose_resolution(meta)
        p_val = c2.split("%")[0]
        return f"{p_val}%"
    return c

def choose_video_audio_options(meta):
    # O usuário pode manter (copy) ou alterar o formato
    c = numeric_or_arrow_choice("Deseja alterar o áudio do vídeo?", ["manter (copy)", "alterar formato de áudio", "Voltar"])
    if c == "Voltar" or c is None:
        return "Voltar", None
    if c == "manter (copy)":
        return None, None
    # alterar formato
    audio_format = choose_audio_format_for_video()
    if audio_format == "Voltar" or audio_format is None:
        return "Voltar", None
    audio_bitrate = choose_audio_bitrate(meta, audio_only_mode=False)
    if audio_bitrate == "Voltar":
        return "Voltar", None
    return audio_format, audio_bitrate

def choose_audio_format_for_video():
    # Aqui pode manter copy pois estamos no vídeo
    c = numeric_or_arrow_choice("Escolha formato de áudio:", ["manter (copy)", "ogg", "mp3", "m4a", "Voltar"])
    if c == "Voltar" or c is None:
        return "Voltar"
    if "manter" in c:
        return None
    return c

def choose_audio_format_for_audio_only():
    # Não há sentido em manter copy, já que vamos extrair áudio do vídeo
    c = numeric_or_arrow_choice("Escolha formato de áudio:", ["ogg", "mp3", "m4a", "Voltar"])
    if c == "Voltar" or c is None:
        return "Voltar"
    return c

def choose_audio_bitrate(meta, audio_only_mode=False):
    # Mostrar original se disponível
    bitrate_choices = []
    if meta["audio_bitrate"]:
        bitrate_choices.append(f"original (~{meta['audio_bitrate']} kbps)")
    # adicionar opções fixas
    fixed_bitrates = ["64k", "96k", "128k", "192k"]
    bitrate_choices.extend(fixed_bitrates)
    bitrate_choices.append("Custom")
    bitrate_choices.append("Voltar")

    c = numeric_or_arrow_choice("Escolha bitrate de áudio:", bitrate_choices)
    if c == "Voltar" or c is None:
        return "Voltar"
    if c.startswith("original"):
        return None
    if c == "Custom":
        val = questionary.text("Digite o bitrate desejado (ex: 160k):").ask()
        if val and (val.endswith("k") and val[:-1].isdigit()):
            return val
        return "Voltar"
    return c
