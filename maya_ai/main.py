import gradio as gr
from maya_ai.orchestrator import Orchestrator
from maya_ai.gaming_orchestrator import GamingOrchestrator
import threading

orchestrator = Orchestrator()
gaming_orchestrator = GamingOrchestrator(orchestrator.brain, orchestrator.skill_manager)

def chat(message, history):
    sarjana_response, durjana_response = orchestrator.run_interaction_cycle([message])
    return f"Sarjana: {sarjana_response}\nDurjana: {durjana_response}"

def start_gaming_loop(goal):
    if not gaming_orchestrator.is_running:
        thread = threading.Thread(target=gaming_orchestrator.start_autonomous_loop, args=(goal,))
        thread.start()
        return "Autonomous gaming loop started."
    return "Autonomous gaming loop is already running."

def stop_gaming_loop():
    if gaming_orchestrator.is_running:
        gaming_orchestrator.stop_autonomous_loop()
        return "Autonomous gaming loop stopped."
    return "Autonomous gaming loop is not running."

with gr.Blocks() as iface:
    with gr.Tab("Chat"):
        gr.ChatInterface(chat)
    with gr.Tab("Gaming"):
        goal_input = gr.Textbox(label="Goal")
        with gr.Row():
            start_button = gr.Button("Start")
            stop_button = gr.Button("Stop")
        status_output = gr.Textbox(label="Status")

        start_button.click(start_gaming_loop, inputs=goal_input, outputs=status_output)
        stop_button.click(stop_gaming_loop, outputs=status_output)

iface.launch()
