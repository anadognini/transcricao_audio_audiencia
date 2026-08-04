# Formatação dos falantes, timestamps e geração do texto final.

import json


def milliseconds_to_timestamp(milliseconds: int) -> str:
    """
    Converte milissegundos para HH:MM:SS.
    """

    total_seconds = int(milliseconds // 1000)

    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60

    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


def format_transcript(transcript_json: dict) -> str:
    """
    Formata a transcrição com timestamps e identificação dos falantes.
    """

    utterances = transcript_json.get("utterances") or []
    lines = []

    for utterance in utterances:
        speaker = utterance.get("speaker", "UNKNOWN")

        start = milliseconds_to_timestamp(
            utterance.get("start", 0)
        )

        end = milliseconds_to_timestamp(
            utterance.get("end", 0)
        )

        text = (utterance.get("text") or "").strip()

        if text:
            lines.append(
                f"[{start} - {end}] SPEAKER_{speaker}: {text}"
            )

    if not lines:
        plain_text = (transcript_json.get("text") or "").strip()

        if plain_text:
            lines.append(plain_text)

    return "\n\n".join(lines)


def transcript_to_json(transcript_json: dict) -> str:
    """
    Converte o resultado bruto da AssemblyAI para uma string JSON.
    """

    return json.dumps(
        transcript_json,
        ensure_ascii=False,
        indent=2,
    )