import gradio as gr
from chatbot import create_chatbot


def launch_ui(vectorstore):
    chat = create_chatbot(vectorstore)
    with gr.Blocks() as demo:
        gr.Markdown("VIB chatbot")
        chatbot = gr.Chatbot(type="messages")
        with gr.Row():
            txt = gr.Textbox(
            show_label=False,
            placeholder="Nhập câu hỏi của bạn..."
        )
        txt.submit(chat, [txt, chatbot], [txt, chatbot])
    return demo
