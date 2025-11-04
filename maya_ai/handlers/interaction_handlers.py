import gradio as gr
import pandas as pd
import asyncio
import threading
import soundfile as sf
import numpy as np

# This is a temporary solution to avoid circular imports.
# In a more advanced structure, we would use a dependency injection pattern.
from maya_ai.main import orchestrator, gaming_orchestrator, proactive_orchestrator, tts_manager, vts_manager, mc_skill, SARJANA_REF, DURJANA_REF

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
    skill = orchestrator.skill_manager.get_skill("Reddit Scraper Skill")
    posts = skill.perform_action("get_top_posts", subreddit_name=subreddit, limit=3)
    topic = f"Discuss the top posts from r/{subreddit}: {', '.join(posts)}"
    return asyncio.run(run_full_interaction(topic, "Discuss these Reddit posts."))

def run_twitter_wrapper(username):
    skill = orchestrator.skill_manager.get_skill("Twitter Scraper Skill")
    tweets = skill.perform_action("get_user_tweets", username=username, limit=3)
    topic = f"Discuss the latest tweets from @{username}: {'; '.join(tweets)}"
    return asyncio.run(run_full_interaction(topic, "Discuss these tweets."))

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

def _format_suggestions_df(suggestions):
    if not suggestions:
        return pd.DataFrame({"ID": [], "Persona": [], "Title": [], "Take": []})

    df = pd.DataFrame({
        "ID": [i for i, _ in enumerate(suggestions)],
        "Persona": [s['persona_name'] for s in suggestions],
        "Title": [s['title'] for s in suggestions],
        "Take": [s['take'] for s in suggestions]
    })
    return df

def _on_select_suggestion(evt: gr.SelectData):
    if evt.index is None:
        return "", "", "", ""

    selected_id = evt.index[0]
    suggestion = proactive_orchestrator.get_suggestions()[selected_id]

    return (
        selected_id,
        suggestion['title'],
        suggestion['url'],
        suggestion['take']
    )

def _refresh_suggestions():
    all_suggestions = proactive_orchestrator.get_suggestions()

    pending = [s for s in all_suggestions if s.get('status', 'pending') == 'pending']
    approved = [s for s in all_suggestions if s.get('status') == 'approved']

    pending_df = _format_suggestions_df(pending)

    if not approved:
        approved_df = pd.DataFrame({"Persona": [], "Title": [], "Final Take": []})
    else:
        approved_df = pd.DataFrame({
            "Persona": [s['persona_name'] for s in approved],
            "Title": [s['title'] for s in approved],
            "Final Take": [s['take'] for s in approved]
        })

    return pending_df, approved_df

def _approve_suggestion(selected_id, edited_take):
    if not selected_id:
        return gr.update(), gr.update(), "", "", "", ""

    suggestion_id = int(selected_id)
    suggestion = proactive_orchestrator.get_suggestions()[suggestion_id]

    suggestion['status'] = 'approved'
    suggestion['take'] = edited_take

    pending_df, approved_df = _refresh_suggestions()

    return pending_df, approved_df, "", "", "", ""

def run_visual_sense_wrapper(prompt):
    """
    Wrapper function to call the Visual Sense skill from the UI.
    """
    skill = orchestrator.skill_manager.get_skill("Visual Sense Skill")
    if not skill:
        return "Error: Visual Sense Skill not found."
    return skill.perform_action("analyze_screen", prompt=prompt)

def _reject_suggestion(selected_id):
    if not selected_id:
        return gr.update(), gr.update(), "", "", "", ""

    suggestion_id = int(selected_id)
    proactive_orchestrator.get_suggestions()[suggestion_id]['status'] = 'rejected'

    pending_df, approved_df = _refresh_suggestions()

    return pending_df, approved_df, "", "", "", ""
