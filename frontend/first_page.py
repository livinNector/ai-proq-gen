import gradio as gr
import ast
from proq_gen.generators.chroma import get_db_store
import json
from proq_gen.convert_to_json import data_to_json
from run import update_question, run_code
from difflib import Differ

from template import make_template_outputs, make_template_testcases

count = 0


def increment_count():
    global count
    count += 1
    return count


def print_n_value(n_value):
    global no_tests
    no_tests = n_value
    return n_value  # Return the value if needed for further processing


def submit_second_page(topic):
    db_store = get_db_store("python-questions", persist_directory="./chroma")
    questions = db_store.similarity_search(topic)
    questions_json = json.loads(data_to_json(questions))
    return questions_json, gr.update(choices=[d["question"] for d in questions_json])


def create_first_page(data_state):
    # solution_visible = gr.State(False)
    with gr.Column(visible=True) as page1:
        gr.Markdown("# Programming in Python")
        with gr.Row():
            with gr.Column(scale=1):
                topic = gr.Textbox(label="Select Topic")
                submit2 = gr.Button("Submit", elem_id="submit2")

                with gr.Tab("Question"):
                    question_select = gr.Dropdown(
                        label="Select Question", choices=[], interactive=True
                    )
                    question_display = gr.Textbox(label="Question", interactive=False)

                with gr.Tab("Test Cases"):
                    testcases_state = gr.Markdown(label="Test Cases")

                with gr.Tab("Output"):
                    outputs_md = gr.Markdown(label="Output")  # JSON output component

                with gr.Tab("Solution 🔒"):
                    solution = gr.Code("Solution Locked")

            with gr.Column(scale=1):
                code_input = gr.Code(
                    label="Write your code here",
                    language="python",
                    lines=10,
                    interactive=True,
                )
                run_button = gr.Button("Run")

        # Connect buttons to functions
        submit2.click(
            fn=submit_second_page, inputs=[topic], outputs=[data_state, question_select]
        )

        question_select.change(
            fn=make_template_testcases,
            inputs=[question_select, data_state],
            outputs=[solution, question_display, testcases_state, code_input],
        )

        run_button.click(
            fn=lambda code, question, data: (
                make_template_outputs(code, question, data)
            ),
            inputs=[code_input, question_select, data_state],
            outputs=[outputs_md],
        )

    return page1, question_select


# Initialize the Gradio app
with gr.Blocks(css=".small-button { padding: 5px 10px; font-size: 12px; }") as demo:
    data_state = gr.State([])

    # First page is now the new topic and question selection interface
    page1_content, question_select = create_first_page(data_state)

demo.launch(share=True)
