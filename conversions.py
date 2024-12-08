def build_ffmpeg_command(input_file, output_file, fps=None, resolution=None, audio_format=None, audio_bitrate=None,
                         video_only=False, audio_only=False):
    """
    Constrói o comando ffmpeg baseado nos parâmetros fornecidos.

    fps: "original" ou um inteiro (ex: 30, 24, 18, 12)
    resolution: "original", "fullhd", "hd", "whatsapp"
    audio_format: "ogg", "mp3", "m4a" (mp4 audio) ou None
    audio_bitrate: ex: "128k", "96k" ou None
    video_only: True/False - se True, remove áudio
    audio_only: True/False - se True, extrai somente o áudio

    Retorna lista com args para ffmpeg.
    """
    cmd = ["-i", input_file]

    # FPS
    if fps and fps != "original":
        cmd += ["-vf", f"fps={fps}"]

    # Resoluções comuns
    scale_map = {
        "fullhd": "1920:1080",
        "hd": "1280:720",
        "whatsapp": "854:480"
    }
    if resolution and resolution in scale_map:
        # Se já existir -vf por causa do fps, precisa concatenar
        vf_found = False
        for i, arg in enumerate(cmd):
            if arg.startswith("-vf"):
                vf_found = True
                cmd[i + 1] = cmd[i + 1] + f",scale={scale_map[resolution]}"
                break
        if not vf_found:
            cmd += ["-vf", f"scale={scale_map[resolution]}"]

    # Se for somente áudio
    if audio_only:
        # remover vídeo (-vn), selecionar codec audio e bitrate
        cmd += ["-vn"]
        if audio_format == "ogg":
            cmd += ["-c:a", "libvorbis"]
        elif audio_format == "mp3":
            cmd += ["-c:a", "libmp3lame"]
        elif audio_format == "m4a":
            cmd += ["-c:a", "aac"]
        else:
            # Default: copy
            cmd += ["-c:a", "copy"]

        if audio_bitrate:
            cmd += ["-b:a", audio_bitrate]
    else:
        # Vídeo
        if video_only:
            cmd += ["-an"]  # sem audio
        else:
            # Para converter áudio dentro do vídeo
            if audio_format:
                if audio_format == "ogg":
                    cmd += ["-c:a", "libvorbis"]
                elif audio_format == "mp3":
                    cmd += ["-c:a", "libmp3lame"]
                elif audio_format == "m4a":
                    cmd += ["-c:a", "aac"]
            else:
                # manter áudio original
                cmd += ["-c:a", "copy"]

            if audio_bitrate:
                cmd += ["-b:a", audio_bitrate]

        # Definir alguns parâmetros de vídeo se quiser otimizar
        # Ex: x264 com crf 23, etc.
        cmd += ["-c:v", "libx264", "-crf", "23", "-preset", "veryslow"]

    cmd += [output_file]
    return cmd
