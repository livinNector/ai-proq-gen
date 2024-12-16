from .equal_check import equal_check_chain
from operator import itemgetter
from langchain_core.runnables import (
    RunnablePassthrough,
    RunnableParallel,
    RunnableLambda,
    RunnableAssign,
)
from .test_case import get_test_case_chain, verify_and_update_testcases

import json


def serialize_metadata(value):
    if isinstance(value, (list, dict)):
        return json.dumps(value)
    return value


def extract_testcases(x):
    testcases = x.get("testcases", {}).get("testcases", [])
    return serialize_metadata(testcases)


extract_text_metadata_chain = {
    "texts": RunnableLambda(itemgetter("statement")).map(),
    "metadatas": RunnableParallel(
        {
            "solution": itemgetter("solution"),
            "question_template": itemgetter("question_template"),
            "function_name": itemgetter("function_name"),
            "tags": lambda x: ",".join(x.get("tags", [])),
            "input_type": itemgetter("input_type"),
            "data_formats": lambda x: ",".join(x.get("data_formats", [])),
            "testcases": extract_testcases,
        }
    ).map(),
}


def get_generator_chain(ideation_chain, testcase_chain, db_store):
    single_item_retriever = db_store.as_retriever(search_kwargs={"k": 1})
    duplicate_check_chain = RunnableParallel(
        {
            "problem": RunnablePassthrough(),
            "statement1": itemgetter("statement"),
            "statement2": itemgetter("statement")
            | single_item_retriever
            | (lambda x: x[0].page_content if x else None),
        }
    ) | RunnablePassthrough.assign(
        is_equal=RunnablePassthrough().pick(["statement1", "statement2"])
        | equal_check_chain
    )

    return (
        ideation_chain
        | duplicate_check_chain.map()
        | {
            "new_problems": (
                lambda problems: [
                    problem for problem in problems if not problem["is_equal"]
                ]
            )
            | (
                RunnablePassthrough().pick("problem")
                | RunnableAssign(
                    {
                        "statement": itemgetter("statement"),
                        "solution": itemgetter("solution"),
                        "testcases": testcase_chain,
                    }
                )
            ).map()
            | extract_text_metadata_chain
            | (lambda x: db_store.add_texts(**x)),
            "duplicate_problems": (
                lambda problems: [
                    problem for problem in problems if problem["is_equal"]
                ]
            ),
        }
    )
