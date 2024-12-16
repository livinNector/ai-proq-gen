from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableAssign
from langchain_core.output_parsers import JsonOutputParser
from langchain_groq import ChatGroq

import json
import random

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
Create ideas for "n_problems" number of problem statements with solutions as json using the mix of below concepts in {lang}.
Also try to mix multiple concepts in the same problem.
The problem statement can have data types, but should not contain any {lang} specific functions or classes.
Resopnd only in JSON. Do not begin with here are the.
Do not output any other string. Just output JSON. No other characters allowed strictly.
""",
        ),
        ("human", "n_problems:4\nideation_concepts:\n{example_concepts}"),
        ("ai", "{examples}"),
        ("human", "n_problems:{n_problems}\n{concepts}"),
    ]
)

model = ChatGroq(temperature=1, model="llama3-70b-8192")

ideation_processor = model | JsonOutputParser()


def get_ideation_chain(
    lang,
    concept_groups: list[tuple[list[str], int]],
    example_concepts: str,
    examples: str,
):
    return (
        RunnableAssign(
            {
                "concepts": lambda x: (
                    concept
                    for concepts, concept_counts in concept_groups
                    for concept in random.choices(concepts, k=concept_counts)
                )
            }
        )
        | prompt.partial(
            lang=lang,
            example_concepts=json.dumps(example_concepts),
            examples=json.dumps(examples),
        )
        | ideation_processor
    )
