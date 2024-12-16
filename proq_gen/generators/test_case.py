from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableAssign, RunnableParallel
from operator import itemgetter
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from langchain_groq import ChatGroq
import subprocess
import sys
import json
import random
import tempfile

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
You are a test case creator. Generate {n_testcases} test cases for the given problem statement in {lang}.
Each test case should include input and expected output.
     Use the function template to generate the test cases. Input should have a suffix code to execute the function. print the repr of the object returned.
Respond only in JSON format. Do not include any additional text. If the solution has a function then the input should contain the code to execute the function. Else 
it should just have normal inputs
""",
        ),
        (
            "human",
            "Problem: Given two integers a and b, find their sum.\nn_testcases: 2\n soltuion : def add(a, b):\n    return a + b\n input_type : code\n",
        ),
        (
            "ai",
            """[
        
    {{
        "input": "print(repr(add(5,7)))",
        "output": "12"
    }},
     {{
        "input": "print(repr(add(10,20)))",
        "output": "30"
     }}
]

""",
        ),
        (
            "human",
            "Problem: Write a program to multiply 2 integers\nn_testcases: 2\n soltuion : a = int(input())\n b = int(input())\nprint(a * b)\n input_type : stdin",
        ),
        (
            "ai",
            """[
        
    {{
        "input": "3 4",
        "output": "12"
    }},
     {{
        "input": "5 6",
        "output": "30"
     }}
]

""",
        ),
        (
            "human",
            "Problem: Given two integers a and b, find their difference.\nn_testcases: 3\n soltuion : def sub(a, b):\n    return a - b\n input_type : code\n",
        ),
        (
            "ai",
            """[
        
    {{
        "input": "print(repr(sub(12,7)))",
        "output": "5"
    }},
     {{
        "input": "print(repr(sub(10,20)))",
        "output": "-10"
     }},
      {{
        "input": "print(repr(sub(100,20)))",
        "output": "80"
     }}
]

""",
        ),
        (
            "human",
            "Problem: Write a program to divide 2 integers\nn_testcases: 2\n soltuion : a = int(input())\n b = int(input())\nprint(a / b)\n input_type : stdin",
        ),
        (
            "ai",
            """[
        
    {{
        "input": "8 4",
        "output": "2.0"
    }},
     {{
        "input": "10 4",
        "output": "2.5"
     }}
]

""",
        ),
        (
            "human",
            "Problem: {statement}\nn_testcases: {n_testcases}\n solution: {solution}\n input_type: {input_type}",
        ),
    ]
)

model = ChatGroq(temperature=0.7, model="llama3-70b-8192")

test_case_processor = model | JsonOutputParser()


# def verify_and_update_testcases(solution, testcases):
#     suffix = """
# import sys
# exec(sys.stdin.read())
# """
#     updated_testcases = []
#     with tempfile.NamedTemporaryFile(delete_on_close=False, mode='w') as f:
#         f.write(solution + suffix)
#         f.close()


#         for testcase in testcases:
#             process = subprocess.run(
#                 [sys.executable, f.name],
#                 input=testcase["input"],
#                 text=True,
#                 capture_output=True,
#             )
#             actual_output = process.stdout.strip()

#         updated_testcase = {
#             "input": testcase["input"],
#             "output": actual_output if actual_output else "Error: No output"
#         }
#         updated_testcases.append(updated_testcase)

#     return updated_testcases


def verify_and_update_testcases(solution, testcases):
    suffix = """
import sys
exec(sys.stdin.read())
"""

    with tempfile.NamedTemporaryFile(delete_on_close=False, mode="w") as f:
        f.write(solution + suffix)
        f.close()

        updated_testcases = []
        for testcase in testcases:
            process = subprocess.run(
                [sys.executable, f.name],
                input=testcase["input"],
                text=True,
                capture_output=True,
            )
            actual_output = process.stdout.strip()

            updated_testcase = {
                "input": testcase["input"],
                "output": actual_output if actual_output else "Error: No output",
            }
            updated_testcases.append(updated_testcase)  # Append each updated test case

    return updated_testcases


def get_test_case_chain(lang, n_testcases):
    partial_prompt = prompt.partial(lang=lang, n_testcases=n_testcases)
    return RunnableParallel(
        {
            "statement": itemgetter("statement"),
            "solution": itemgetter("solution"),
            "input_type": itemgetter("input_type"),
            "testcases": RunnableParallel(
                {
                    "generated_testcases": partial_prompt | test_case_processor,
                    "solution": itemgetter("solution"),
                }
            )
            | (
                lambda x: verify_and_update_testcases(
                    x["solution"], x["generated_testcases"]
                )
            ),
        }
    )


#


# test_case_chain = get_test_case_chain(
#     lang="Python",
#     n_testcases=4
# )


# result = test_case_chain.invoke({"problem_statement":"Write a function that takes a string and returns its reverse.", "solution":"def reverse_string(s):\n    return s[::-1]"})
# print(json.dumps(result, indent=2))
