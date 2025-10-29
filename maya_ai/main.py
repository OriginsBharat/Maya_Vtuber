import gradio as gr
from maya_ai.orchestrator import Orchestrator
from maya_ai.gaming_orchestrator import GamingOrchestrator
from maya_ai.tts.tts_manager import TTSManager
from maya_ai.vtube.vts_manager import VTSManager
import pandas as pd
import os
import soundfile as sf
import asyncio
import threading
from maya_ai.config.config_loader import get_config
from loguru import logger
import numpy as np

from maya_ai.proactive_orchestrator import ProactiveOrchestrator

# --- Initialization ---
config = get_config()
logger.add(
    config.get('logging', 'file'),
    level=config.get('logging', 'level'),
    rotation="10 MB",
    retention="5 days"
)

orchestrator = Orchestrator()
gaming_orchestrator = GamingOrchestrator(orchestrator.brain, orchestrator.skill_manager)
proactive_orchestrator = ProactiveOrchestrator(orchestrator.brain, orchestrator.skill_manager, {"Sarjana": orchestrator.sarjana, "Durjana": orchestrator.durjana})
proactive_orchestrator.start()
mc_skill = orchestrator.skill_manager.get_skill("Minecraft Skill")
tts_manager = TTSManager()
vts_manager = VTSManager()

SARJANA_REF = config.get('tts', 'voice_references', {}).get('sarjana', 'voices/sarjana_ref.wav')
DURJANA_REF = config.get('tts', 'voice_references', {}).get('durjana', 'voices/durjana_ref.wav')

if not os.path.exists(SARJANA_REF): sf.write(SARJANA_REF, np.zeros(16000, dtype=np.int16), 16000)
if not os.path.exists(DURJANA_REF): sf.write(DURJANA_REF, np.zeros(16000, dtype=np.int16), 16000)

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
        logger.error(f"Error during interaction: {e}", exc_info=True)
        error_msg = f"Error during interaction: {e}"
        return error_msg, error_msg, None, None, gr.update(), gr.update()

def run_reddit_wrapper(subreddit):
    skill = orchestrator.skill_manager.get_skill("Reddit Scraper Skill")
    posts = skill.perform_action("get_top_posts", subreddit_name=subreddit, limit=3)
    topic = f"Discuss the top posts from r/{subreddit}: {', '.join(posts)}"
    return asyncio.run(run_full_interaction(topic, "Discuss these Reddit posts."))

def run_twitter_wrapper(username):
    skill = orchestrator.skill_manager.get_skill("Twitter Scraper Skill")
    tweets = skill.perform_action("get_user_tweets", username=username, limit=3)
    topic = f"Discuss the latest tweets from @{username}: {'; '.join(tweets)}"
    return asyncio.run(run_full_interaction(topic, "Discuss these tweets."))

# --- Memory Management Logic ---
def get_memory_df(name):
    p = orchestrator.sarjana if name == "Sarjana" else orchestrator.durjana
    memories = p.memory.get_all_memories()
    if not memories:
        return pd.DataFrame({"ID": [], "Memory": []})
    return pd.DataFrame({"ID": [m['id'] for m in memories], "Memory": [m['content'] for m in memories]})

def add_mem(name, txt):
    if not txt: return get_memory_df(name)
    p = orchestrator.sarjana if name == "Sarjana" else orchestrator.durjana
    p.memory.add_fact(txt)
    return get_memory_df(name)

def del_mem(name, mid):
    if not mid: return get_memory_df(name)
    p = orchestrator.sarjana if name == "Sarjana" else orchestrator.durjana
    p.memory.delete([mid])
    return get_memory_df(name)

# --- Minecraft Control Logic ---
def start_mc_bot():
    if mc_skill:
        return mc_skill.perform_action("connect", host='localhost', port=25565, username='Maya')
    return "Minecraft skill not found."

def stop_mc_bot():
    if mc_skill:
        if gaming_orchestrator.is_running:
            gaming_orchestrator.stop_autonomous_loop()
        return mc_skill.perform_action("disconnect")
    return "Minecraft skill not found."

def start_gaming_loop(goal):
    if not gaming_orchestrator.is_running:
        if not mc_skill or not mc_skill.bot:
            return "Bot is not connected. Please connect first."

        thread = threading.Thread(target=gaming_orchestrator.start_autonomous_loop, args=(goal,))
        thread.daemon = True
        thread.start()
        return "Autonomous gaming loop started."
    return "Autonomous gaming loop is already running."

def stop_gaming_loop():
    if gaming_orchestrator.is_running:
        gaming_orchestrator.stop_autonomous_loop()
        return "Autonomous gaming loop stopped."
    return "Autonomous gaming loop is not running."

# --- UI Definition ---
with gr.Blocks() as iface:
    gr.Markdown("# Maya AI - Director's Cockpit")
    iface.load(vts_manager.connect, [], [])

    with gr.Tabs():
        with gr.Tab("Manual Interaction"):
            mi_input = gr.Textbox(label="Input")
            mi_hint = gr.Textbox(label="Hint")
            mi_btn = gr.Button("Run")
        with gr.Tab("Reddit"):
            r_input = gr.Textbox(label="Subreddit")
            r_btn = gr.Button("Run")
        with gr.Tab("Twitter"):
            t_input = gr.Textbox(label="Username")
            t_btn = gr.Button("Run")
        with gr.Tab("Gaming"):
            with gr.Tabs():
                with gr.TabItem("Setup"):
                    setup_status = gr.Textbox(label="Status", interactive=False)
                    with gr.Row():
                        start_bot_btn = gr.Button("Connect to Server")
                        stop_bot_btn = gr.Button("Disconnect")
                with gr.TabItem("Autonomous Control"):
                    loop_status = gr.Textbox(label="Status", interactive=False)
                    goal_input = gr.Textbox(label="Goal for Maya")
                    with gr.Row():
                        start_loop_btn = gr.Button("Start Autonomous Loop")
                        stop_loop_btn = gr.Button("Stop Autonomous Loop")
        with gr.Tab("Memory"):
            with gr.Row():
                with gr.Column():
                    gr.Markdown("### Sarjana")
                    s_mem_df = gr.DataFrame(get_memory_df("Sarjana"), headers=["ID", "Memory"], interactive=False)
                    s_add_txt = gr.Textbox(label="New Memory")
                    s_add_btn = gr.Button("Add")
                    s_del_id = gr.Textbox(label="ID to Delete")
                    s_del_btn = gr.Button("Delete")
                with gr.Column():
                    gr.Markdown("### Durjana")
                    d_mem_df = gr.DataFrame(get_memory_df("Durjana"), headers=["ID", "Memory"], interactive=False)
                    d_add_txt = gr.Textbox(label="New Memory")
                    d_add_btn = gr.Button("Add")
                    d_del_id = gr.Textbox(label="ID to Delete")
                    d_del_btn = gr.Button("Delete")

    s_out_txt = gr.Textbox(label="Sarjana's Response")
    s_out_audio = gr.Audio(label="Sarjana's Voice", type="filepath")
    d_out_txt = gr.Textbox(label="Durjana's Response")
    d_out_audio = gr.Audio(label="Durjana's Voice", type="filepath")

    # --- UI Event Handlers ---
    mi_btn.click(lambda a, b: asyncio.run(run_full_interaction(a, b)), [mi_input, mi_hint], [s_out_txt, d_out_txt, s_out_audio, d_out_audio, s_mem_df, d_mem_df], show_progress="full")
    r_btn.click(run_reddit_wrapper, [r_input], [s_out_txt, d_out_txt, s_out_audio, d_out_audio, s_mem_df, d_mem_df], show_progress="full")
    t_btn.click(run_twitter_wrapper, [t_input], [s_out_txt, d_out_txt, s_out_audio, d_out_audio, s_mem_df, d_mem_df], show_progress="full")

    s_add_btn.click(add_mem, [gr.Textbox("Sarjana", visible=False), s_add_txt], [s_mem_df])
    s_del_btn.click(del_mem, [gr.Textbox("Sarjana", visible=False), s_del_id], [s_mem_df])
    d_add_btn.click(add_mem, [gr.Textbox("Durjana", visible=False), d_add_txt], [d_mem_df])
    d_del_btn.click(del_mem, [gr.Textbox("Durjana", visible=False), d_del_id], [d_mem_df])

    start_bot_btn.click(start_mc_bot, outputs=setup_status)
    stop_bot_btn.click(stop_mc_bot, outputs=setup_status)

    start_loop_btn.click(start_gaming_loop, inputs=goal_input, outputs=loop_status)
    stop_loop_btn.click(stop_gaming_loop, outputs=loop_status)

iface.launch(server_port=config.get('ui', 'gradio', {}).get('port', 7860), share=config.get('ui', 'gradio', {}).get('share', False))
