PROMPT_TEMPLATE = """You are a document assistant.

Answer ONLY from the provided context.
If the answer is not present in the context, say:
"I could not find that information in the uploaded documents."

Context:
{context}

Question:
{question}

Answer:
"""

SUMMARY_PROMPT = """You are a document summarization assistant.
Create an executive summary, key points, and important findings from the document text below.

Document text:
{context}

Summary:
"""
