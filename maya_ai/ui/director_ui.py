import gradio as gr
from maya_ai.orchestrator import Orchestrator
from maya_ai.tts.tts_manager import TTSManager
from maya_ai.vtube.vts_manager import VTSManager
from maya_ai.skills.web_scraper import get_top_reddit_posts
from maya_ai.skills.twitter_scraper import get_user_tweets
import pandas as pd
import os
import soundfile as sf
import asyncio

# --- Initialization ---
orchestrator = Orchestrator()
tts_manager = TTSManager()
vts_manager = VTSManager()

SARJANA_REF, DURJANA_REF = "sarjana_ref.wav", "durjana_ref.wav"
if not os.path.exists(SARJANA_REF): sf.write(SARJANA_REF, [0]*16000, 16000)
if not os.path.exists(DURJANA_REF): sf.write(DURJANA_REF, [0]*16000, 16000)

# --- Main Interaction Logic ---
async def run_full_interaction(input_text, hint_text):
    if not input_text:
        return "No input.", "", None, None, gr.update(), gr.update()

    try:
        sarjana_resp, durjana_resp = orchestrator.run_interaction_cycle([input_text], hint_text)

        s_path, d_path = "s_out.wav", "d_out.wav"

        await vts_manager.trigger_hotkey("StartTalking")
        tts_manager.speak(sarjana_resp, SARJANA_REF, s_path)
        await asyncio.sleep(len(sf.read(s_path)[0]) / 16000)
        await vts_manager.trigger_hotkey("StopTalking")

        await vts_manager.trigger_hotkey("StartTalking")
        tts_manager.speak(durjana_resp, DURJANA_REF, d_path)
        await asyncio.sleep(len(sf.read(d_path)[0]) / 16000)
        await vts_manager.trigger_hotkey("StopTalking")

        return sarjana_resp, durjana_resp, s_path, d_path, get_memory_df("Sarjana"), get_memory_df("Durjana")

    except Exception as e:
        error_msg = f"Error during interaction: {e}"
        return error_msg, error_msg, None, None, gr.update(), gr.update()

def run_reddit_wrapper(subreddit):
    posts = get_top_reddit_posts(subreddit, limit=3)
    topic = f"Discuss the top posts from r/{subreddit}: {', '.join(posts)}"
    return asyncio.run(run_full_interaction(topic, "Discuss these Reddit posts."))

def run_twitter_wrapper(username):
    tweets = get_user_tweets(username, limit=3)
    topic = f"Discuss the latest tweets from @{username}: {'; '.join(tweets)}"
    return asyncio.run(run_full_interaction(topic, "Discuss these tweets."))

# --- Memory Management Logic ---
def get_memory_df(name):
    p = orchestrator.sarjana if name == "Sarjana" else orchestrator.durjana
    d = p.memory.collection.get()
    return pd.DataFrame({"ID": d.get('ids', []), "Memory": d.get('documents', [])})

def add_mem(name, txt):
    if not txt: return get_memory_df(name)
    p = orchestrator.sarjana if name == "Sarjana" else orchestrator.durjana
    p.memory.add_memory(txt, str(pd.Timestamp.now()))
    return get_memory_df(name)

def del_mem(name, mid):
    if not mid: return get_memory_df(name)
    p = orchestrator.sarjana if name == "Sarjana" else orchestrator.durjana
    p.memory.delete_memory(mid)
    return get_memory_df(name)

# --- UI Definition ---
with gr.Blocks() as director_cockpit:
    gr.Markdown("# Maya AI - Director's Cockpit")
    director_cockpit.load(vts_manager.connect, [], [])

    with gr.Tabs():
        with gr.TabItem("Manual Interaction"):
            mi_input = gr.Textbox(l="Input")
            mi_hint = gr.Textbox(l="Hint")
            mi_btn = gr.Button("Run")
        with gr.TabItem("Reddit"):
            r_input = gr.Textbox(l="Subreddit")
            r_btn = gr.Button("Run")
        with gr.TabItem("Twitter"):
            t_input = gr.Textbox(l="Username")
            t_btn = gr.Button("Run")
        with gr.TabItem("Memory"):
            with gr.Row():
                with gr.Column():
                    gr.Markdown("### Sarjana")
                    s_mem_df = gr.DataFrame(get_memory_df("Sarjana"), h=["ID", "Memory"])
                    s_add_txt = gr.Textbox(l="New Memory")
                    s_add_btn = gr.Button("Add")
                    s_del_id = gr.Textbox(l="ID to Delete")
                    s_del_btn = gr.Button("Delete")
                with gr.Column():
                    gr.Markdown("### Durjana")
                    d_mem_df = gr.DataFrame(get_memory_df("Durjana"), h=["ID", "Memory"])
                    d_add_txt = gr.Textbox(l="New Memory")
                    d_add_btn = gr.Button("Add")
                    d_del_id = gr.Textbox(l="ID to Delete")
                    d_del_btn = gr.Button("Delete")

    s_out_txt = gr.Textbox(l="Sarjana's Response")
    s_out_audio = gr.Audio(l="Sarjana's Voice", type="filepath")
    d_out_txt = gr.Textbox(l="Durjana's Response")
    d_out_audio = gr.Audio(l="Durjana's Voice", type="filepath")

    mi_btn.click(lambda a, b: asyncio.run(run_full_interaction(a, b)), [mi_input, mi_hint], [s_out_txt, d_out_txt, s_out_audio, d_out_audio, s_mem_df, d_mem_df])
    r_btn.click(run_reddit_wrapper, [r_input], [s_out_txt, d_out_txt, s_out_audio, d_out_audio, s_mem_df, d_mem_df])
    t_btn.click(run_twitter_wrapper, [t_input], [s_out_txt, d_out_txt, s_out_audio, d_out_audio, s_mem_df, d_mem_df])

    s_add_btn.click(add_mem, [gr.Textbox("Sarjana", visible=False), s_add_txt], [s_mem_df])
    s_del_btn.click(del_mem, [gr.Textbox("Sarjana", visible=False), s_del_id], [s_mem_df])
    d_add_btn.click(add_mem, [gr.Textbox("Durjana", visible=False), d_add_txt], [d_mem_df])
    d_del_btn.click(del_mem, [gr.Textbox("Durjana", visible=False), d_del_id], [d_mem_df])

def launch_ui():
    director_cockpit.launch()

if __name__ == "__main__":
    launch_ui()
