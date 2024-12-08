import os
import subprocess
import requests
import zipfile
import shutil

FFMPEG_URL = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
FFMPEG_DIR = "ffmpeg-bin"

def is_ffmpeg_available():
    """Verifica se o ffmpeg está no PATH ou no diretório local."""
    if shutil.which("ffmpeg"):
        return True
    # Verifica se existe no diretório local também
    local_ffmpeg = os.path.join(FFMPEG_DIR, "ffmpeg.exe")
    return os.path.exists(local_ffmpeg)

def download_and_extract_ffmpeg():
    """Baixa e extrai o ffmpeg para a pasta ffmpeg-bin."""
    os.makedirs(FFMPEG_DIR, exist_ok=True)
    zip_path = os.path.join(FFMPEG_DIR, "ffmpeg.zip")
    print("Baixando ffmpeg...")
    r = requests.get(FFMPEG_URL, stream=True)
    with open(zip_path, 'wb') as f:
        for chunk in r.iter_content(chunk_size=8192):
            f.write(chunk)
    print("Download concluído. Extraindo...")
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(FFMPEG_DIR)
    os.remove(zip_path)
    # A pasta extraída pode ter um nome grande, procurar o ffmpeg e mover para o ffmpeg-bin
    for root, dirs, files in os.walk(FFMPEG_DIR):
        if "ffmpeg.exe" in files:
            # mover todos os .exe principais para FFMPEG_DIR raiz
            for exe in ["ffmpeg.exe", "ffprobe.exe", "ffplay.exe"]:
                exe_path = os.path.join(root, exe)
                if os.path.exists(exe_path):
                    shutil.move(exe_path, os.path.join(FFMPEG_DIR, exe))
            break
    print("ffmpeg instalado no diretório local.")

def get_ffmpeg_command():
    """Retorna o comando ffmpeg completo com path, se necessário."""
    if shutil.which("ffmpeg"):
        return "ffmpeg"
    else:
        # usar o local
        return os.path.join(FFMPEG_DIR, "ffmpeg.exe")

def ensure_ffmpeg():
    """Garante que o ffmpeg esteja disponível, senão faz o download."""
    if not is_ffmpeg_available():
        download_and_extract_ffmpeg()
