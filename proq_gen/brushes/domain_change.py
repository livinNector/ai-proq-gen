from langchain_core.runnables import RunnableLambda
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_groq import ChatGroq


model = ChatGroq(temperature=0.7, model="llama3-70b-8192")

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
Given a text content in any format, 
change the content to a similar content in the given target domain.
Respond only with the modified content. Use the same format as the input for the output
""",
        ),
        (
            "human",
            """
content: 
Find the maximum
target: cinema""",
        ),
        (
            "ai",
            """
Determine the highest-grossing movie from a collection of films.
""",
        ),
        (
            "human",
            '''
content: 
"""What is this?"""
target: transport''',
        ),
        ("ai", '''"""What car is this?"""'''),
        ("human", "content:{content}\ntarget: {domain}"),
    ]
)

domain_change = prompt | model | StrOutputParser()
