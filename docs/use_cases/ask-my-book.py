import pickle
from pathlib import Path
from time import perf_counter

from langchain import OpenAI, PromptTemplate
from langchain.chains import ChatVectorDBChain
from langchain.chains.llm import LLMChain
# Load pages of the book
from langchain.chains.question_answering import load_qa_chain


t0 = perf_counter()

# Load data
if not Path("vectorstore.pkl").exists():
    raise ValueError("vectorstore.pkl does not exist, please run ingest.py first")
with open("vectorstore.pkl", "rb") as f:
    global vectorstore
    vectorstore = pickle.load(f)
t1 = perf_counter()

# Define prompts
condense_question_prompt = """Given the following conversation and a follow up question, rephrase the follow up question to be a standalone question.

Chat History:
{chat_history}
Follow Up Input: {question}
Standalone question:"""
CONDENSE_QUESTION_PROMPT = PromptTemplate.from_template(condense_question_prompt)

prompt_template = """Use the following pieces of context to answer the question at the end. If you don't know the answer, just say that you don't know, don't try to make up an answer.

{context}

Question: {question}
Helpful Answer:"""
QA_PROMPT = PromptTemplate(
    template=prompt_template, input_variables=["context", "question"]
)

# Load Chain

doc_chain = load_qa_chain(OpenAI(temperature=0, verbose=True),
                          chain_type="stuff",
                          prompt=QA_PROMPT,
                          verbose=True)
question_chain = LLMChain(  # Chain to condense previous input
    llm=OpenAI(temperature=0, verbose=True),
    prompt=CONDENSE_QUESTION_PROMPT,
)
qa_custom = ChatVectorDBChain(
    vectorstore=vectorstore,
    combine_docs_chain=doc_chain,
    question_generator=question_chain,
)

# Use chain
chat_history = []
result = qa_custom(
    {"question": "What is specific knowledge", "chat_history": chat_history}
)
chat_history = [(result["question"], result["answer"])]
print("answer 1:", result["answer"])
print("Loading DB: ", t1 - t0)
print("Test: ", t1 - t0)
print("Total: ", perf_counter() - t0)