# The Maya AI Project

Welcome to the Maya AI Project, a sophisticated, dual-persona AI VTuber designed for autonomous content creation.

## About The Project

Maya is an AI VTuber with two distinct, independent Indian personas: **Sarjana** ('sanskari but naughty') and **Durjana** ('chaotic gremlin'). The core of the project is a "two minds" system where these personas can interact with each other, livestream chat, and a private "director's channel."

This project is built to be 100% free and run locally, using Ollama to power the Large Language Models.

## Features

*   **Dual-Persona System:** Two independent AI agents, Sarjana and Durjana, with unique and editable personalities.
*   **YAML Configuration:** Easily manage all project settings through a simple `config.yaml` file.
*   **Secure Secret Management:** All API keys are managed securely using a `.env` file.
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

Follow the `QUICKSTART.md` for the fastest way to get started. This guide provides more detailed information.

### 1. Set Up Your API Keys (One-Time Setup)

This project uses free services that require API keys. You will need to create free accounts for each.

1.  **Copy the Example `.env` file:**
    ```bash
    cp .env.example .env
    ```
2.  **Edit the `.env` file and add your keys:**
    *   `PINECONE_API_KEY`: Get this from [pinecone.io](https://pinecone.io) after creating a free account.
    *   `REDDIT_CLIENT_ID` & `REDDIT_CLIENT_SECRET`: Create a new "script" app at [reddit.com/prefs/apps](https://www.reddit.com/prefs/apps).
    *   `TWITTER_BEARER_TOKEN`: Get this from the [Twitter Developer Portal](https://developer.twitter.com/).

### 2. Local Environment Setup

*   **Install Python 3.11:** This project requires Python 3.11. If you don't have it, we recommend using `pyenv` for Windows to manage Python versions.
*   **Install Dependencies:** Open a terminal in the project root directory and run:
    ```bash
    pip install -r requirements.txt
    ```

### 3. Index TTS Setup (For Voice Generation)

This is the most complex part of the setup. Follow these instructions carefully.

1.  **Download the Models:** You need to download the pre-trained models for Index TTS. You can find them here: [Index TTS v1.9B Pre-trained Models](https://huggingface.co/X-LANCE/Index-1.9B-v2/tree/main).
    *   Download `config.yaml`.
    *   Download `pytorch_model.bin`.

2.  **Place Models in the Correct Directory:**
    *   Make sure you are in the project's root directory.
    *   The models you downloaded must be placed inside the `vendor/index-tts/checkpoints/` directory.
    *   Verify the final structure:
        ```
        vendor/
        └── index-tts/
            └── checkpoints/
                ├── config.yaml
                └── pytorch_model.bin
        ```

3.  **Record Voice References:**
    *   Record a short (`~10-15 seconds`) audio clip of the voices you want for Sarjana and Durjana.
    *   Save them as `.wav` files and place them in the `voices/` directory.
    *   Update your `config.yaml` file to point to these new files.

### 4. Running the Application

1.  **Start Ollama:** Ensure your local Ollama server is running and you have pulled the correct model: `ollama pull llama3.1:8b`.
2.  **Start VTube Studio:** If you want to see the avatar, have VTube Studio open with the API enabled.
3.  **Launch the Director's Cockpit:** In a terminal at the project root, run:
    ```bash
    python maya_ai/main.py
    ```
4.  Open your web browser to the URL provided by the script (usually `http://127.0.0.1:7861`). You are now ready to direct Maya!

## Troubleshooting

*   **`ModuleNotFoundError: No module named 'maya_ai'`:** You are not running the command from the project's root directory. `cd` to the root and try again.
*   **`ModuleNotFoundError: No module named 'indextts'`:** The `PYTHONPATH` is not set correctly. The `python maya_ai/main.py` command should handle this automatically, but if you are using a different method, you may need to set it manually: `export PYTHONPATH=.
vendor/`.
*   **TTS Errors:**
    *   "Config file not found" or "Model file not found": You have not placed the downloaded `config.yaml` and `pytorch_model.bin` files in the correct `vendor/index-tts/checkpoints/` directory.
    *   Low-quality or robotic voice: Your voice reference clips may be too short or have too much background noise. Try recording a clearer, longer sample.
*   **`ValueError: PINECONE_API_KEY not found`:** You have not created your `.env` file or have not added your Pinecone API key to it.
