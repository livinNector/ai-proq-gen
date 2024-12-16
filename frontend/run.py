import gradio as gr
import os
import json
import ast
import requests
from difflib import Differ
from jinja2 import Template, Environment


def update_question(selected_question, data):

    if data is None or not data:
        return "", "", "", "", "", ""
    selected_data = next(d for d in data if d["question"] == selected_question)
    function_template = selected_data["question_template"].replace("\\n", "\n")
    # print(selected_data)
    return (
        selected_data["solution"],
        selected_data["question"],
        selected_data["testcases"],
        function_template,
    )


def run_code(code_snippet, test_cases, input_type="stdin"):

    actual_output_messages = []
    expected_output_messages = []
    if input_type == "code":
        code_snippet += "\nimport sys; exec(sys.stdin.read())"

    # print(code_snippet)
    for test_case in test_cases:

        expected_output = test_case["output"]
        payload = {
            "language": "python",
            "version": "3.10.0",
            "files": [{"name": "script.py", "content": code_snippet}],
            "stdin": test_case["input"],
        }

        response = requests.post("https://emkc.org/api/v2/piston/execute", json=payload)
        execution_result = response.json()

        actual_output = (
            execution_result["run"]["output"].strip()
            if "run" in execution_result and "output" in execution_result["run"]
            else ""
        )
        actual_output_messages.append(actual_output)

        expected_output_messages.append(expected_output)

    output_json = {
        "actual_output": actual_output_messages,
        "expected_output": expected_output_messages,
    }
    return output_json
