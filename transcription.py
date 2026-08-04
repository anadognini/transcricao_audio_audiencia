import time
from pathlib import Path
from typing import Callable

import requests


BASE_URL = "https://api.assemblyai.com/v2"


def upload_audio(
    file_path: Path,
    api_key: str,
) -> str:
    """
    Envia o áudio para a AssemblyAI.

    Retorna a URL temporária criada pela API.
    """

    headers = {
        "authorization": api_key,
        "content-type": "application/octet-stream",
    }

    try:
        with file_path.open("rb") as audio_file:
            response = requests.post(
                f"{BASE_URL}/upload",
                headers=headers,
                data=audio_file,
                timeout=600,
            )

        response.raise_for_status()

    except requests.RequestException as error:
        raise RuntimeError(
            "Não foi possível enviar o áudio para a AssemblyAI."
        ) from error

    response_data = response.json()

    upload_url = response_data.get("upload_url")

    if not upload_url:
        raise RuntimeError(
            "A AssemblyAI não retornou a URL do áudio enviado."
        )

    return upload_url


def submit_transcript(
    audio_url: str,
    api_key: str,
    language_code: str | None = "pt",
    speaker_labels: bool = True,
) -> str:
    """
    Cria uma solicitação de transcrição na AssemblyAI.

    Retorna o identificador da transcrição.
    """

    headers = {
        "authorization": api_key,
        "content-type": "application/json",
    }

    payload = {
        "audio_url": audio_url,
        "speaker_labels": speaker_labels,
        "punctuate": True,
        "format_text": True,
    }

    if language_code:
        payload["language_code"] = language_code

    try:
        response = requests.post(
            f"{BASE_URL}/transcript",
            headers=headers,
            json=payload,
            timeout=60,
        )

        response.raise_for_status()

    except requests.RequestException as error:
        raise RuntimeError(
            "Não foi possível iniciar a transcrição na AssemblyAI."
        ) from error

    response_data = response.json()

    transcript_id = response_data.get("id")

    if not transcript_id:
        raise RuntimeError(
            "A AssemblyAI não retornou o identificador da transcrição."
        )

    return transcript_id


def poll_transcript(
    transcript_id: str,
    api_key: str,
    poll_interval_seconds: int = 5,
    timeout_seconds: int = 7200,
    status_callback: Callable[[str], None] | None = None,
) -> dict:
    """
    Consulta periodicamente o status da transcrição.

    Retorna o JSON completo quando o processamento terminar.
    """

    headers = {
        "authorization": api_key,
    }

    deadline = time.time() + timeout_seconds

    while True:
        try:
            response = requests.get(
                f"{BASE_URL}/transcript/{transcript_id}",
                headers=headers,
                timeout=60,
            )

            response.raise_for_status()

        except requests.RequestException as error:
            raise RuntimeError(
                "Não foi possível consultar o andamento da transcrição."
            ) from error

        transcript_data = response.json()
        status = transcript_data.get("status")

        if status_callback:
            status_callback(status or "unknown")

        if status == "completed":
            return transcript_data

        if status == "error":
            error_message = transcript_data.get(
                "error",
                "Erro desconhecido."
            )

            raise RuntimeError(
                f"A AssemblyAI não conseguiu concluir a transcrição: "
                f"{error_message}"
            )

        if time.time() > deadline:
            raise TimeoutError(
                "A transcrição excedeu o tempo máximo de espera."
            )

        time.sleep(poll_interval_seconds)