import gradio as gr
import time
import run_query

# Placeholder function to simulate getting a response from an LLM
def get_response(prompt):

    output = run_query.query_rag(prompt)
    # Simulate a delay to mimic response time from an LLM
    # time.sleep(2)
    # Return a simulated response
    return output

# Function to handle the chat interaction
def chat_interface(prompt, history):
    history = history or []
    history.append((prompt, "..."))  # Append the prompt with a placeholder
    response = get_response(prompt)  # Get the response from the LLM
    history[-1] = (prompt, response)  # Replace the placeholder with the actual response
    return history, history

# Create a Gradio Blocks interface
with gr.Blocks() as demo:
    gr.Markdown("## Chat with an LLM")
    chatbot = gr.Chatbot()
    message = gr.Textbox(label="Your prompt:")
    state = gr.State([])  # Initialize the state to store the conversation history

    # Define the submit button and its functionality
    submit_btn = gr.Button("Send")
    submit_btn.click(chat_interface, inputs=[message, state], outputs=[chatbot, state])

# Launch the app
demo.launch()
