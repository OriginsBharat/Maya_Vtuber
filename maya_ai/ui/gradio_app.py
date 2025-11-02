import gradio as gr
import pandas as pd
import asyncio

# Import handlers
from maya_ai.handlers.interaction_handlers import (
    run_full_interaction,
    run_reddit_wrapper,
    run_twitter_wrapper,
    get_memory_df,
    add_mem,
    del_mem,
    start_mc_bot,
    stop_mc_bot,
    start_gaming_loop,
    stop_gaming_loop,
    _refresh_suggestions,
    _on_select_suggestion,
    _approve_suggestion,
    _reject_suggestion
)
from maya_ai.vtube.vts_manager import VTSManager

def launch_ui(config, vts_manager):
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
            with gr.Tab("Proactive Creator"):
                pc_refresh_btn = gr.Button("Refresh Suggestions")
                with gr.Row():
                    with gr.Column():
                        gr.Markdown("### New Suggestions")
                        pc_suggestions_df = gr.DataFrame(headers=["ID", "Persona", "Title", "Take"], interactive=True, row_count=(5), col_count=(4), wrap=True, visible_cols=[False, True, True, True])

                        gr.Markdown("#### Edit Suggestion")
                        pc_selected_id = gr.Textbox(label="Selected ID", interactive=False)
                        pc_selected_title = gr.Textbox(label="Title", interactive=False)
                        pc_selected_url = gr.Textbox(label="Source URL", interactive=False)
                        pc_edit_take = gr.Textbox(label="Edit Take", lines=3)
                        with gr.Row():
                            pc_approve_btn = gr.Button("Approve")
                            pc_reject_btn = gr.Button("Reject")

                    with gr.Column():
                        gr.Markdown("### Approved Queue")
                        pc_approved_df = gr.DataFrame(headers=["Persona", "Title", "Final Take"], interactive=False, row_count=(10), col_count=(3), wrap=True)

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

        pc_suggestions_df.select(_on_select_suggestion, None, [pc_selected_id, pc_selected_title, pc_selected_url, pc_edit_take])
        pc_refresh_btn.click(_refresh_suggestions, None, [pc_suggestions_df, pc_approved_df])
        pc_approve_btn.click(_approve_suggestion, [pc_selected_id, pc_edit_take], [pc_suggestions_df, pc_approved_df, pc_selected_id, pc_selected_title, pc_selected_url, pc_edit_take])
        pc_reject_btn.click(_reject_suggestion, [pc_selected_id], [pc_suggestions_df, pc_approved_df, pc_selected_id, pc_selected_title, pc_selected_url, pc_edit_take])

    iface.launch(server_port=config.get('ui', 'gradio', {}).get('port', 7860), share=config.get('ui', 'gradio', {}).get('share', False))
