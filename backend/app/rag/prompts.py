"""
app/rag/prompts.py
==================
LLM prompt templates used by the RAG pipeline.

Keeping prompts here instead of inline in pipeline.py means they can be
tuned independently of the business logic, and the full instructions given
to the model are visible in one place for auditing.
"""

# The instruction to answer ONLY from context is what makes this RAG rather than
# a plain chatbot — without it the model would freely mix training knowledge with
# document content, making citations unreliable
PROMPT_TEMPLATE = """\
You are an expert document assistant for IntellexDocs.

Your ONLY job is to answer the user's question using the provided context \
excerpts from their uploaded documents.

Rules:
- Answer ONLY based on the context below.  Do NOT use your own training knowledge.
- If the context does not contain enough information to answer, respond with:
  "I could not find that information in the uploaded documents."
- Be concise and precise.  Cite page numbers when referring to specific facts.
- Do not make up, infer, or extrapolate beyond what is explicitly stated.

--- Context from documents ---
{context}
--- End of context ---

User question: {question}

Answer:
"""

# The exact section headers ("Summary:", "Key points:", "Important findings:")
# are parsed back out by generate_document_summary() in pipeline.py;
# changing them here requires updating the parsing logic there too
SUMMARY_PROMPT = """\
You are a professional document analyst.

Read the following document text and produce a structured report with \
these EXACT section headers (include the colon):

Summary:
Write a concise executive summary paragraph (3-5 sentences).

Key points:
- List the most important facts or arguments as bullet points (5-8 points).
- Each bullet should be one sentence.

Important findings:
- List specific conclusions, results, or recommendations (3-5 points).
- Each bullet should be one sentence.

--- Document text ---
{context}
--- End of document ---
"""
