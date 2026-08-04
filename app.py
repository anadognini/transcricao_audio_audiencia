# Interface Streamlit, upload do vídeo, mensagens e downloads.

from pathlib import Path
import tempfile

import streamlit as st

from audio import extract_audio
from formatter import format_transcript, transcript_to_json
from transcription import (
    poll_transcript,
    submit_transcript,
    upload_audio,
)


st.set_page_config(
    page_title="Transcrição de Audiências",
    page_icon="/workspaces/transcricao_audio_audiencia/assets/logo3.png",
    layout="centered",
)


st.title("Transcrição de Audiências")

st.write(
    "Envie o vídeo de uma audiência para extrair o áudio e gerar "
    "uma transcrição com identificação dos falantes e timestamps."
)


try:
    ASSEMBLYAI_API_KEY = st.secrets["ASSEMBLYAI_API_KEY"]
except KeyError:
    st.error(
        "A chave ASSEMBLYAI_API_KEY não foi configurada nos "
        "secrets do Streamlit."
    )
    st.stop()


uploaded_file = st.file_uploader(
    "Envie o vídeo da audiência",
    type=["mp4", "mov", "mkv", "avi"],
    help="Formatos aceitos: MP4, MOV, MKV e AVI.",
)


speaker_labels = st.checkbox(
    "Identificar diferentes falantes",
    value=True,
    help=(
        "Quando ativado, a transcrição tenta separar as falas "
        "entre SPEAKER_A, SPEAKER_B e assim por diante."
    ),
)


st.warning(
    "O vídeo e o áudio serão enviados para processamento pela AssemblyAI. "
    "Não feche esta página enquanto a transcrição estiver sendo realizada."
)


if uploaded_file is not None:
    file_size_mb = uploaded_file.size / (1024 * 1024)

    st.write(f"**Arquivo:** {uploaded_file.name}")
    st.write(f"**Tamanho:** {file_size_mb:.2f} MB")

    start_button = st.button(
        "Iniciar transcrição",
        type="primary",
        use_container_width=True,
    )

    if start_button:
        status_placeholder = st.empty()
        progress_bar = st.progress(0)

        try:
            with tempfile.TemporaryDirectory() as temporary_directory:
                temp_dir = Path(temporary_directory)

                original_suffix = (
                    Path(uploaded_file.name).suffix.lower() or ".mp4"
                )

                safe_stem = Path(uploaded_file.name).stem

                video_path = temp_dir / f"video{original_suffix}"
                wav_path = temp_dir / f"{safe_stem}.wav"
                mp3_path = temp_dir / f"{safe_stem}.mp3"

                status_placeholder.info(
                    "Salvando o vídeo temporariamente..."
                )
                progress_bar.progress(5)

                with video_path.open("wb") as video_file:
                    video_file.write(uploaded_file.getbuffer())

                status_placeholder.info(
                    "Extraindo e preparando o áudio..."
                )
                progress_bar.progress(15)

                extract_audio(
                    video_path=video_path,
                    wav_path=wav_path,
                    mp3_path=mp3_path,
                )

                status_placeholder.info(
                    "Enviando o áudio para a AssemblyAI..."
                )
                progress_bar.progress(30)

                upload_url = upload_audio(
                    file_path=wav_path,
                    api_key=ASSEMBLYAI_API_KEY,
                )

                status_placeholder.info(
                    "Solicitando a transcrição..."
                )
                progress_bar.progress(40)

                transcript_id = submit_transcript(
                    audio_url=upload_url,
                    api_key=ASSEMBLYAI_API_KEY,
                    language_code="pt",
                    speaker_labels=speaker_labels,
                )

                def update_transcription_status(status: str) -> None:
                    status_messages = {
                        "queued": (
                            "A transcrição está na fila de processamento..."
                        ),
                        "processing": (
                            "A AssemblyAI está transcrevendo o áudio..."
                        ),
                    }

                    message = status_messages.get(
                        status,
                        f"Status da transcrição: {status}",
                    )

                    status_placeholder.info(message)
                    progress_bar.progress(65)

                transcript_result = poll_transcript(
                    transcript_id=transcript_id,
                    api_key=ASSEMBLYAI_API_KEY,
                    poll_interval_seconds=5,
                    timeout_seconds=7200,
                    status_callback=update_transcription_status,
                )

                status_placeholder.info(
                    "Formatando os arquivos..."
                )
                progress_bar.progress(90)

                formatted_text = format_transcript(
                    transcript_result
                )

                raw_json = transcript_to_json(
                    transcript_result
                )

                mp3_bytes = mp3_path.read_bytes()

                st.session_state["transcription_result"] = {
                    "filename": safe_stem,
                    "text": formatted_text,
                    "json": raw_json,
                    "mp3": mp3_bytes,
                }

                progress_bar.progress(100)

                status_placeholder.success(
                    "Transcrição concluída com sucesso."
                )

        except Exception as error:
            progress_bar.empty()
            status_placeholder.error(
                f"Não foi possível concluir o processamento: {error}"
            )


if "transcription_result" in st.session_state:
    result = st.session_state["transcription_result"]

    st.divider()

    st.subheader("Transcrição")

    st.text_area(
        "Resultado",
        value=result["text"],
        height=400,
    )

    st.subheader("Downloads")

    first_column, second_column, third_column = st.columns(3)

    with first_column:
        st.download_button(
            label="Baixar transcrição",
            data=result["text"],
            file_name=f"{result['filename']}_transcricao.txt",
            mime="text/plain",
            use_container_width=True,
        )

    with second_column:
        st.download_button(
            label="Baixar áudio",
            data=result["mp3"],
            file_name=f"{result['filename']}.mp3",
            mime="audio/mpeg",
            use_container_width=True,
        )

    with third_column:
        st.download_button(
            label="Baixar JSON",
            data=result["json"],
            file_name=f"{result['filename']}_resultado.json",
            mime="application/json",
            use_container_width=True,
        )

    if st.button(
        "Limpar resultado",
        use_container_width=True,
    ):
        del st.session_state["transcription_result"]
        st.rerun()