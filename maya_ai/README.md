# The Maya AI Project

Welcome to the Maya AI Project, a sophisticated, dual-persona AI VTuber designed for autonomous content creation.

## About The Project

Maya is an AI VTuber with two distinct, independent Indian personas: **Sarjana** ('sanskari but naughty') and **Durjana** ('chaotic gremlin'). The core of the project is a "two minds" system where these personas can interact with each other, livestream chat, and a private "director's channel."

This project is built to be 100% free and run locally, using Ollama to power the Large Language Models.

## Features

*   **Dual-Persona System:** Two independent AI agents, Sarjana and Durjana, with unique and editable personalities.
*   **Cloud Configuration Vault:** Securely manage all your API keys (Pinecone, Reddit, Twitter) in a central cloud vault powered by Supabase. Run Maya from any computer with just one set of credentials.
*   **Cloud-Based Long-Term Memory:** Maya's consciousness lives in the cloud, powered by Pinecone. Her memory is persistent and scalable.
*   **Director's Cockpit UI:** A beginner-friendly web interface to:
    *   Interact with the personas.
    *   Inject real-time "hints" to guide conversations.
    *   Manually manage the long-term memory of each persona.
*   **Social Media Integration:**
    *   **Reddit:** Fetch and discuss the top posts from any subreddit.
    *   **Twitter:** Fetch and discuss the latest tweets from any user.
*   **Live Chat Integration:** Connect to a live YouTube stream and interact with the audience.
*   **Voice & Body Ready:** Includes a fully functional Text-to-Speech (TTS) engine and integration with VTube Studio for lip-sync.

## Setup and Installation Guide

Follow these steps to get the Maya AI Project running on your Windows 11 machine.

### 1. Set Up Your Cloud Services (One-Time Setup)

This project uses free cloud services to manage configuration and memory. You will need to create a free account for each.

*   **Supabase (Cloud Config Vault):**
    1.  Go to [supabase.com](https://supabase.com) and create a free account.
    2.  Create a new project.
    3.  Inside your project, go to the "Table Editor" and create a new table named `config`.
    4.  This table must have two text columns: `key` and `value`.
    5.  Populate this table with the API keys for the other services (see below).
    6.  Go to "Project Settings" -> "API" and find your **Project URL** and your `service_role` **Secret Key**.

*   **Pinecone (Cloud Memory):**
    1.  Go to [pinecone.io](https://pinecone.io) and create a free account.
    2.  In the Pinecone console, find your **API Key**.
    3.  Add this key to your Supabase `config` table with the key name `PINECONE_API_KEY`.

*   **Reddit & Twitter:**
    1.  Create developer accounts for Reddit and X (Twitter) to get your API credentials.
    2.  Add these credentials to your Supabase `config` table with the following key names: `REDDIT_CLIENT_ID`, `REDDIT_CLIENT_SECRET`, `TWITTER_BEARER_TOKEN`.

### 2. Local Environment Setup

*   **Install Python 3.11:** This project requires Python 3.11. If you don't have it, we recommend using `pyenv` for Windows to manage Python versions.
*   **Set Environment Variables:** You must set two environment variables to connect to your Cloud Config Vault:
    *   `SUPABASE_URL`: Your project URL from Supabase.
    *   `SUPABASE_KEY`: Your `service_role` secret key from Supabase.
*   **Install Dependencies:** Open a terminal in the `maya_ai` project directory and run:
    ```bash
    pip install -r requirements.txt
    ```

### 3. Running the Application

1.  **Start Ollama:** Ensure your local Ollama server is running.
2.  **Start VTube Studio:** If you want to see the avatar, have VTube Studio open with the API enabled.
3.  **Launch the Director's Cockpit:** In a terminal at the `maya_ai` project root, run:
    ```bash
    PYTHONPATH=. python3 ui/director_ui.py
    ```
4.  Open your web browser to the URL provided by the script (usually `http://127.0.0.1:7860`). You are now ready to direct Maya!
