# Get Maya Running in 5 Minutes

1.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

2.  **Create `.env` file:**

    Copy the example file:
    ```bash
    cp .env.example .env
    ```
    Now, open the `.env` file and fill in your API keys:
    ```
    PINECONE_API_KEY=your_key
    REDDIT_CLIENT_ID=your_id
    REDDIT_CLIENT_SECRET=your_secret
    TWITTER_BEARER_TOKEN=your_token
    ```

3.  **Run Maya:**
    ```bash
    python maya_ai/main.py
    ```

4.  **Open your browser:**

    Navigate to `http://localhost:7861`

5.  **Type "Hello Maya!" in the Manual Interaction tab and click "Run".**

Done! You're talking to Maya.
