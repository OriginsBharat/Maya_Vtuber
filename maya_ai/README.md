# The Maya AI Project

Welcome to the Maya AI Project, a sophisticated, dual-persona AI VTuber designed for autonomous content creation.

## About The Project

Maya is an AI VTuber with two distinct, independent Indian personas: **Sarjana** ('sanskari but naughty') and **Durjana** ('chaotic gremlin'). The core of the project is a "two minds" system where these personas can interact with each other, livestream chat, and a private "director's channel."

This project is built to be 100% free and run locally, using Ollama to power the Large Language Models.

## Features

*   **Dual-Persona System:** Two independent AI agents, Sarjana and Durjana, with unique and editable personalities.
*   **YAML Configuration:** Easily manage all project settings through a simple `config.yaml` file.
*   **Robust Logging:** All major events are logged to a file using `loguru` for easy debugging.
*   **Cloud-Based Long-Term Memory:** Maya's consciousness lives in the cloud, powered by Pinecone. Her memory is persistent and scalable.
*   **Director's Cockpit UI:** A beginner-friendly web interface to:
    *   Interact with the personas.
    *   Inject real-time "hints" to guide conversations.
    *   Manually manage the long-term memory of each persona.
    *   Control the autonomous Minecraft agent.
*   **Social Media Integration:**
    *   **Reddit:** Fetch and discuss the top posts from any subreddit.
    *   **Twitter:** Fetch and discuss the latest tweets from any user.
*   **Live Chat Integration:** Connect to a live YouTube stream and interact with the audience.
*   **Voice & Body Ready:** Includes a fully functional Text-to-Speech (TTS) engine (Index TTS) and integration with VTube Studio for lip-sync.

## Setup and Installation Guide

Follow these steps to get the Maya AI Project running on your Windows 11 machine.

### 1. Set Up Your Cloud Services (One-Time Setup)

This project uses free cloud services to manage configuration and memory. You will need to create a free account for each.

*   **Pinecone (Cloud Memory):**
    1.  Go to [pinecone.io](https://pinecone.io) and create a free account.
    2.  In the Pinecone console, find your **API Key**.

*   **Reddit & Twitter:**
    1.  Create developer accounts for Reddit and X (Twitter) to get your API credentials.

### 2. Local Environment Setup

*   **Install Python 3.11:** This project requires Python 3.11. If you don't have it, we recommend using `pyenv` for Windows to manage Python versions.
*   **Create `config.yaml`:** In the project root, create a copy of `config.example.yaml` and name it `config.yaml`. Open this new file and fill in your API keys from Pinecone, Reddit, and Twitter.
*   **Install Dependencies:** Open a terminal in the `maya_ai` project directory and run:
    ```bash
    pip install -r requirements.txt
    ```
*   **Index TTS Setup:** This project uses Index TTS. Please follow the setup instructions on the official [Index TTS GitHub repository](https://github.com/X-LANCE/Index-1.9B) to download the necessary models and place them in the `vendor/index-tts/checkpoints` directory.

### 3. Running the Application

1.  **Start Ollama:** Ensure your local Ollama server is running.
2.  **Start VTube Studio:** If you want to see the avatar, have VTube Studio open with the API enabled.
3.  **Launch the Director's Cockpit:** In a terminal at the project root, run:
    ```bash
    PYTHONPATH=. python3 maya_ai/main.py
    ```
4.  Open your web browser to the URL provided by the script (usually `http://127.0.0.1:7860`). You are now ready to direct Maya!

## Configuration Reference

The `config.yaml` file is the central place to manage all settings for the Maya AI Project. Here's a brief overview of the available options:

| Section | Key | Description |
|---|---|---|
| `brain` | `model` | The name of the Ollama model to use for the AI's brain. |
| `tts` | `model_dir` | The directory where the Index TTS models are stored. |
| `memory` | `embedding_model` | The Sentence Transformers model to use for creating memory embeddings. |
| `personas` | `sarjana.prompt_file` | The path to the system prompt file for the Sarjana persona. |
| `ui` | `gradio.port` | The port to run the Gradio web UI on. |
| `logging` | `level` | The minimum logging level to output (e.g., "INFO", "DEBUG"). |
| `paths` | `voices` | The directory to store voice reference files. |

## Troubleshooting

*   **`ModuleNotFoundError`:** If you get this error when running the application, make sure you are running the command from the project root and that you have set the `PYTHONPATH` correctly.
*   **TTS Errors:** If you are having trouble with the TTS, make sure you have followed the Index TTS setup instructions correctly and that the model files are in the correct directory.
*   **Pinecone Errors:** If you are having trouble with Pinecone, make sure you have set your `PINECONE_API_KEY` correctly in the `config.yaml` file.
