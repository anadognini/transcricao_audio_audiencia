# Extração e conversão do áudio com FFmpeg.

from pathlib import Path
import ffmpeg

def extract_audio(
    video_path: Path,
    wav_path: Path,
    mp3_path: Path,
) -> None:
    """
    Extrai o áudio de um vídeo em dois formatos:

    - WAV mono, 16 kHz: usado para a transcrição;
    - MP3 mono, 16 kHz: disponibilizado para download.
    """

    try:
        input_stream = ffmpeg.input(str(video_path))

        normalized_audio = input_stream.audio.filter("dynaudnorm")

        (
            ffmpeg
            .output(
                normalized_audio,
                str(wav_path),
                format="wav",
                acodec="pcm_s16le",
                ac=1,
                ar=16000,
            )
            .overwrite_output()
            .run(quiet=True)
        )

        (
            ffmpeg
            .output(
                normalized_audio,
                str(mp3_path),
                format="mp3",
                acodec="libmp3lame",
                ac=1,
                ar=16000,
                audio_bitrate="64k",
            )
            .overwrite_output()
            .run(quiet=True)
        )

    except ffmpeg.Error as error:
        stderr = error.stderr.decode("utf-8", errors="replace") if error.stderr else ""

        raise RuntimeError(
            f"Não foi possível extrair o áudio do vídeo.\n\n{stderr}"
        ) from error

    if not wav_path.exists():
        raise FileNotFoundError(
            f"O arquivo WAV não foi criado: {wav_path}"
        )

    if not mp3_path.exists():
        raise FileNotFoundError(
            f"O arquivo MP3 não foi criado: {mp3_path}"
        )
    
