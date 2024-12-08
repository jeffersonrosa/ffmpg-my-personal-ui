Interface de linha de comando em Python para converter vídeos e áudios usando ffmpeg, com opções simplificadas de fps, dimensões, formatos de áudio e taxas de bits. Inclui verificação e instalação automática do ffmpeg no Windows 10, caso não esteja disponível.

## Recursos

- Escolha de fps: original, 30, 24, 18, 12.
- Resoluções comuns: original, FullHD (1920x1080), HD (1280x720), WhatsApp (854x480), etc.
- Formatos de áudio: ogg, mp3, mp4 (somente áudio), com taxas comuns (128k, 96k).
- Conversão individual ou em lote.
- Verificação e instalação automática do ffmpeg se não encontrado.

## Requisitos

- Python 3.x
- Windows 10 (testado, pode funcionar em outros ambientes)
- [requests](https://pypi.org/project/requests/) (para download automático do ffmpeg)

Instale dependências com:
```bash
pip install -r requirements.txt
```

## Uso

Execute:
```bash
python main.py
```

Siga as instruções do menu interativo.

## Notas

- O script tentará fazer o download do ffmpeg caso não encontre a instalação local.
- Você pode ajustar o link e a versão do ffmpeg no arquivo `ffmpeg_installer.py`.

## Licença

Este projeto é licenciado sob a Licença MIT - consulte o arquivo [LICENSE](LICENSE) para detalhes.