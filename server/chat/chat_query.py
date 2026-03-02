import os
import asyncio
from dotenv import load_dotenv
from pinecone import Pinecone
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_core.prompts import PromptTemplate
from langchain_groq import ChatGroq
from server.config.db import chunk_collection

load_dotenv()

# all environments

GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
PINECONE_API_KEY = os.getenv('PINECONE_API_KEY')
PINECONE_INDEX_NAME = os.getenv('PINECONE_INDEX_NAME', 'tutor-rags') 

GROQ_API_KEY = os.getenv('GROQ_API_KEY')

os.environ['GOOGLE_API_KEY'] = GOOGLE_API_KEY

# 1. Initialize pinecone client
pc = Pinecone(api_key=PINECONE_API_KEY)
index = pc.Index(PINECONE_INDEX_NAME)

# 2. Define embedding model
embed_model = GoogleGenerativeAIEmbeddings(model='models/gemini-embedding-001')

# 3. Define LLM model
llm = ChatGroq(
    temperature=0.3,
    model_name='llama-3.3-70b-versatile',
    groq_api_key=GROQ_API_KEY
)

# 4. Define chat prompt
rag_prompt = PromptTemplate.from_template(
    """
You are a helpful educational assistant.
Answer the question using ONLY the context below.

Question:
{question}

Context:
{context}

If relevant, mention the document source.

"""
)

# 5. Define RAG chain
rag_chain = rag_prompt | llm

# 6. Define chat function
async def answer_query(query: str, user_role: str, user_grade: int) -> dict:
    # 1. Embedding generation
    embedding = await asyncio.to_thread(embed_model.embed_query, query)

    # 2. Retrieve relevant embedding from vector database
    results = await asyncio.to_thread(
        index.query, 
        vector=embedding, 
        top_k=5,
        include_metadata=True,
        filter={
            # "grade": user_grade,   # it is to check for exact grade
            "grade": {"$lte": user_grade},
            'role': {"$in": ['Public', user_role]}
        }
    )

    # 3. Validation check
    if not results.get('matches'):
        return {
            'answer': 'No relevant documents found.',
            'sources': []
        }
    
    # 4. Retrieve context form mongodb

    # 4.1 Get chunk ids
    chunk_ids = [m['id'] for m in results['matches']]

    # 4.2 Get document/text
    docs = list(chunk_collection.find({'chunk_id': {'$in': chunk_ids}}))

    # 4.3 validation check
    if not docs:
        return {
            'answer': 'Context unavailable.',
            'sources': []
        }
    
    # 4.4 Preserve context order
    # 4.4.1
    doc_map = {d['chunk_id']: d for d in docs}
    ordered_map = [doc_map[cid] for cid in chunk_ids if cid in doc_map]

    # 4.4.2
    context = '\n\n\n'.join(d['text'] for d in ordered_map)
    sources = list({d['source'] for d in ordered_map})

    # 4.5 Gather response
    response = await asyncio.to_thread(
        rag_chain.invoke,
        {'question': query, 'context': context}
    )

    # 5 Get proper answer
    answer_text = (
        response.content
        if hasattr(response, 'content')
        else str(response)
    )

    return {
        'answer': answer_text,
        'sources': sources
    }
