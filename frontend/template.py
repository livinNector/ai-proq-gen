import gradio as gr
import os
import json
import ast
import requests
from difflib import Differ
from jinja2 import Template, Environment


# output_json = {"actual_output": actual_output_messages, "expected_output":expected_output_messages }
# input,
def make_template_testcases(selected_question, data):
    from run import update_question

    solution, question_display, testcases, code_input = update_question(
        selected_question, data
    )
    testcases_template = Template(
        """
    {% for testcase in  testcases %}
    ### Input {{loop.index}}
    ```
    {{testcase.input}}
    ```
    ### Expected Output {{loop.index}}
    ```
    {{testcase.output}}
    ```  

                                                                    
    {% endfor %}
    """
    )
    return (
        solution,
        question_display,
        testcases_template.render(testcases=testcases),
        code_input,
    )


def make_template_outputs(code_snippet, selected_question, test_data):
    from run import run_code

    selected_data = next(
        (item for item in test_data if item["question"] == selected_question), None
    )
    test_cases = selected_data["testcases"]
    input_type = selected_data["input_type"]

    output_json = run_code(code_snippet, test_cases, input_type)

    def zip_filter(a, b):
        return zip(a, b)

    env = Environment()
    env.filters["zip"] = zip_filter

    output_template = env.from_string(
        """
    {% set list1 = output_json['actual_output'] %}
    {% set list2 = output_json['expected_output'] %}
    {% for item1, item2 in list1 | zip(list2) %}
        ### Actual Output {{loop.index}}                    
        {% if item1 == item2 %}
            Passed ✅
        {% else %}
            Expected: {{ item2 }}, but got: {{ item1 }} ❌
        {% endif %}                
    {% endfor %}

    """
    )

    return output_template.render(output_json=output_json)
