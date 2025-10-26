import gradio as gr
from maya_ai.orchestrator import Orchestrator
# TTS and VTS are still disabled to avoid the dependency issue
# from maya_ai.tts.tts_manager import TTSManager
# from maya_ai.vtube.vts_manager import VTSManager
from maya_ai.skills.web_scraper import get_top_reddit_posts
import pandas as pd
import os
import soundfile as sf
import asyncio
import time

# --- Initialization ---
orchestrator = Orchestrator()
# tts_manager = TTSManager()
# vts_manager = VTSManager()

# --- Main Logic ---
def run_interaction(input_text, hint_text):
    if not input_text:
        return "No input provided.", "", gr.update(), gr.update()

    try:
        sarjana_resp, durjana_resp = orchestrator.run_interaction_cycle([input_text], hint_text)
    except Exception as e:
        # Provide a much clearer error message if the backend fails
        error_message = f"An error occurred while communicating with the AI Brain (Ollama): {e}. Please ensure the Ollama server is running and accessible."
        return error_message, error_message, gr.update(), gr.update()

    s_mem_df = get_memory_df('Sarjana')
    d_mem_df = get_memory_df('Durjana')

    # Return None for audio paths as TTS is disabled
    return sarjana_resp, durjana_resp, None, None, s_mem_df, d_mem_df

def run_reddit_interaction(subreddit):
    if not subreddit:
        return "Please enter a subreddit.", "", None, None, gr.update(), gr.update()

    posts = get_top_reddit_posts(subreddit, limit=3)
    topic = f"The top posts on r/{subreddit} are: {', '.join(posts)}"
    return run_interaction(topic, "Discuss these Reddit posts.")

# --- Memory Management Logic ---
def get_memory_df(persona_name):
    persona = orchestrator.sarjana if persona_name == "Sarjana" else orchestrator.durjana
    try:
        memories_data = persona.memory.collection.get()
        if not memories_data or not memories_data['ids']:
            return pd.DataFrame({"ID": [], "Memory": []})
        return pd.DataFrame({"ID": memories_data['ids'], "Memory": memories_data['documents']})
    except Exception as e:
        print(f"Error getting memory for {persona_name}: {e}")
        return pd.DataFrame({"ID": ["ERROR"], "Memory": [str(e)]})


def add_memory(persona_name, memory_text):
    if not memory_text: return get_memory_df(persona_name)
    persona = orchestrator.sarjana if persona_name == "Sarjana" else orchestrator.durjana
    import uuid
    memory_id = str(uuid.uuid4())
    persona.memory.add_memory(memory_text, memory_id)
    return get_memory_df(persona_name)

def delete_memory(persona_name, memory_id):
    if not memory_id: return get_memory_df(persona_name)
    persona = orchestrator.sarjana if persona_name == "Sarjana" else orchestrator.durjana
    persona.memory.delete_memory(memory_id)
    return get_memory_df(persona_name)

# --- Define the Full Gradio Interface ---
with gr.Blocks() as director_cockpit:
    gr.Markdown("# Maya AI - Director's Cockpit (TTS Disabled)")

    with gr.Tabs():
        with gr.TabItem("Manual Interaction"):
            chat_input = gr.Textbox(label="Simulated Input", placeholder="Type a message or topic...")
            hint_input = gr.Textbox(label="Director's Hint (Optional)")
            manual_submit = gr.Button("Run Manual Interaction")

        with gr.TabItem("Reddit Content"):
            subreddit_input = gr.Textbox(label="Subreddit", placeholder="e.g., memes")
            reddit_submit_button = gr.Button("Fetch & Discuss Reddit Posts")

        with gr.TabItem("Memory Management"):
            with gr.Row():
                with gr.Column():
                    gr.Markdown("### Sarjana's Memory")
                    s_memory_df = gr.DataFrame(get_memory_df("Sarjana"), headers=["ID", "Memory"], interactive=False, max_rows=10)
                    with gr.Row():
                        s_new_memory_text = gr.Textbox(label="New Memory")
                        s_add_button = gr.Button("Add")
                    with gr.Row():
                        s_delete_id = gr.Textbox(label="Memory ID to Delete")
                        s_delete_button = gr.Button("Delete")

                with gr.Column():
                    gr.Markdown("### Durjana's Memory")
                    d_memory_df = gr.DataFrame(get_memory_df("Durjana"), headers=["ID", "Memory"], interactive=False, max_rows=10)
                    with gr.Row():
                        d_new_memory_text = gr.Textbox(label="New Memory")
                        d_add_button = gr.Button("Add")
                    with gr.Row():
                        d_delete_id = gr.Textbox(label="Memory ID to Delete")
                        d_delete_button = gr.Button("Delete")

    with gr.Row():
        sarjana_output = gr.Textbox(label="Sarjana's Response", interactive=False)
        durjana_output = gr.Textbox(label="Durjana's Response", interactive=False)

    # --- Event Wiring ---
    manual_submit.click(
        fn=run_interaction,
        inputs=[chat_input, hint_input],
        outputs=[sarjana_output, durjana_output, s_memory_df, d_memory_df]
    )
    reddit_submit_button.click(
        fn=run_reddit_interaction,
        inputs=[subreddit_input],
        outputs=[sarjana_output, durjana_output, s_memory_df, d_memory_df]
    )
    s_add_button.click(fn=add_memory, inputs=[gr.Textbox("Sarjana", visible=False), s_new_memory_text], outputs=s_memory_df)
    s_delete_button.click(fn=delete_memory, inputs=[gr.Textbox("Sarjana", visible=False), s_delete_id], outputs=s_memory_df)
    d_add_button.click(fn=add_memory, inputs=[gr.Textbox("Durjana", visible=False), d_new_memory_text], outputs=d_memory_df)
    d_delete_button.click(fn=delete_memory, inputs=[gr.Textbox("Durjana", visible=False), d_delete_id], outputs=d_memory_df)

def launch_ui():
    director_cockpit.launch()

if __name__ == "__main__":
    launch_ui()
