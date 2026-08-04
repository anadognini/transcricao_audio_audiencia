<p align="center">
  <img src="assets/Captura%20de%20tela%202026-08-04%20150636.png" width="900">
</p>

---

# ⚖️ Transcrição de Audiências
Aplicação web desenvolvida em **Python** com **Streamlit** para automatizar a transcrição de vídeos de audiências utilizando a API da **AssemblyAI**.

A aplicação permite que usuários enviem um vídeo diretamente pelo navegador, realizando automaticamente a extração do áudio, a transcrição com diarização (identificação dos falantes) e a geração de arquivos para download.

## Funcionalidades

- Upload de vídeos (`.mp4`, `.mov`, `.mkv` e `.avi`)
- Extração automática do áudio utilizando FFmpeg
- Transcrição automática via AssemblyAI
- Diarização (identificação dos diferentes falantes)
- Inclusão de timestamps em cada fala
- Download da transcrição em `.txt`
- Download do áudio extraído em `.mp3`
- Download da resposta completa da API em `.json`

## Interface

A aplicação foi desenvolvida utilizando Streamlit, permitindo que qualquer usuário realize a transcrição sem necessidade de executar scripts manualmente.

Fluxo da aplicação:

```text
Upload do vídeo
        │
        ▼
Extração do áudio (FFmpeg)
        │
        ▼
Envio para AssemblyAI
        │
        ▼
Transcrição + Diarização
        │
        ▼
Formatação do resultado
        │
        ▼
Download dos arquivos
```

## Tecnologias utilizadas

- Python 3
- Streamlit
- FFmpeg
- Requests
- AssemblyAI API

## Estrutura do projeto

```text
.
├── app.py                 # Interface Streamlit
├── audio.py               # Extração do áudio
├── transcription.py       # Comunicação com a API da AssemblyAI
├── formatter.py           # Formatação da transcrição
├── assets/                # Logos e imagens
├── requirements.txt
├── packages.txt
└── .streamlit/
```

## Como executar localmente

Clone o repositório:

```bash
git clone https://github.com/SEU-USUARIO/NOME-DO-REPOSITORIO.git
```

Entre na pasta:

```bash
cd NOME-DO-REPOSITORIO
```

Crie um ambiente virtual:

```bash
python -m venv .venv
```

Ative o ambiente:

Windows

```bash
.venv\Scripts\activate
```

Linux/macOS

```bash
source .venv/bin/activate
```

Instale as dependências:

```bash
pip install -r requirements.txt
```

Crie o arquivo:

```text
.streamlit/secrets.toml
```

Adicione sua chave da AssemblyAI:

```toml
ASSEMBLYAI_API_KEY="SUA_CHAVE"
```

Execute a aplicação:

```bash
streamlit run app.py
```

## Observações

A chave da AssemblyAI **não é armazenada no repositório**.

Ela deve ser configurada através de:

- `.streamlit/secrets.toml` durante o desenvolvimento local;
- **Secrets** do Streamlit Community Cloud durante o deploy.

## Licença

Este projeto foi desenvolvido para fins educacionais e de automação de fluxos de transcrição de audiências para uso particular.
