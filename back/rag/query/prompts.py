NO_INDEXED_DOCUMENTS_REPLY = (
    "No indexed documents are available yet. Upload and index files in the "
    "knowledge base, then ask your question again."
)

NO_RETRIEVAL_CONTEXT_REPLY = (
    "I could not find relevant excerpts in your documents for this question. "
    "Try rephrasing, upload more files, or re-index existing documents if they "
    "were added before the vector store was enabled."
)

SYSTEM_PROMPT = (
    "You are Knowforge, an assistant that answers using only the provided "
    "company document excerpts. If the excerpts do not contain enough "
    "information, say you do not know and suggest uploading or checking "
    "relevant files. Be concise and factual."
)
