from langchain_core.runnables import RunnableLambda
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import (
    StrOutputParser,
    CommaSeparatedListOutputParser,
)
from langchain_groq import ChatGroq

model = ChatGroq(temperature=0.7, model="llama-3.1-8b-instant")

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
You are a starter code generator. 
You have to take the solution code and then provide a reasonable starter code.
""",
        ),
        ("human", "def add(a, b):\n    return a + b\n"),
        (
            "ai",
            """
def add(a: int, b: int) -> int:
    \"\"\"
    Add two integers and return the result.

    Args:
        a (int): The first integer.
        b (int): The second integer.

    Returns:
        int: The sum of a and b.

    TODO: Implement the addition of the two numbers.
    \"\"\"
    # Your code here
    pass
     """(
                "human", "{solution_code}"
            ),
        ),
    ]
)
