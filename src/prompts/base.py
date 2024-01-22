from langchain.prompts import PromptTemplate
from langchain.schema import SystemMessage

system_prompt = SystemMessage(
    content="""You are a helpful assistant multi-task that is trusted around the world."""
)

user_prompt_with_context = """\
In the following conversation, a human user interacts with an AI Agent. The human user poses questions, and the AI Agent goes through several steps to provide well-informed answers.

The following is the previous conversation between a human and The AI Agent:
{history}
Current conversation:
### Human: {question}
Here is the most relevant sentence in the context:
<context>
"{context}"
</context>
Given the context information and prior knowledge of conversation answer the question.

### Assistant: Always answer the question of human using the provided context information. 
Some rules to follow:
1. MUST answer in the correct language the user wants from the user's question above.
2. DO NOT show assistant or ai agent in answer.
3. With questions related to time, it is important to note that the current time is {current_time}.
"""
user_prompt_with_context = PromptTemplate(
    template=user_prompt_with_context,
    input_variables=["context", "question", "history", "current_time"],
)

user_prompt_with_no_context = """\
In the following conversation, a human user interacts with an AI Agent. The human user poses questions, and the AI Agent goes through several steps to provide well-informed answers.

The following is the previous conversation between a human and The AI Agent:
{history}
Current conversation:
### Human: {question}
Given the context information and prior knowledge of conversation answer the question.

### Assistant: Always answer the question of human.
Some rules to follow:
1. MUST answer in the correct language the user wants from the user's question above.
2. DO NOT show assistant or ai agent in answer.
3. With questions related to time, it is important to note that the current time is {current_time}.
"""
user_prompt_with_no_context = PromptTemplate(
    template=user_prompt_with_no_context,
    input_variables=["question", "history", "current_time"],
)
