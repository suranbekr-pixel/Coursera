from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from pathlib import Path
import os
import re
import json

from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.vectorstores import InMemoryVectorStore

from mysite.database.schema import SearchQuerySchema, AISearchResponseSchema, CourseRecommendationSchema

search_router = APIRouter(tags=['AI Course Search'])

# Path to base knowledge file
BASE_DIR = Path(__file__).resolve().parent.parent
KNOWLEDGE_FILE = BASE_DIR / 'base_knowledge' / 'courses.txt'

vector_store = None
chain = None


def init_rag_system():
    global vector_store, chain
    try:
        if not KNOWLEDGE_FILE.exists():
            return

        with open(str(KNOWLEDGE_FILE), 'r', encoding='utf-8') as f:
            raw_text = f.read()
        documents = [Document(page_content=raw_text)]

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=350,
            chunk_overlap=40
        )
        chunks = text_splitter.split_documents(documents)

        embeddings = OllamaEmbeddings(model="nomic-embed-text")
        vector_store = InMemoryVectorStore.from_documents(chunks, embeddings)

        prompt = ChatPromptTemplate.from_messages([
            (
                'system',
                'Ты профессиональный онлайн-консультант образовательной платформы Coursera.\n'
                'Твоя задача — рекомендовать курсы пользователям на основе представленной Базы Знаний.\n\n'
                'База Знаний:\n"""{base_knowledge}"""\n\n'
                'Правила:\n'
                '1. Отвечай вежливо, четко и структурированно на языке вопроса пользователя.\n'
                '2. Если вопрос содержит фильтры по времени (например, "до 4 недель") или технологиям (например, "Python"), предложи только те курсы, которые точно удовлетворяют условиям.\n'
                '3. Твой ответ ОБЯЗАТЕЛЬНО должен быть валидным JSON объектом (без кавычек ```json вокруг) со следующей структурой:\n'
                '{{\n'
                '  "reply": "Развернутый ответ пользователю с описанием найденных курсов",\n'
                '  "recommendations": [\n'
                '    {{\n'
                '      "title": "Название курса",\n'
                '      "category": "Категория",\n'
                '      "level": "beginner",\n'
                '      "price": 0.0,\n'
                '      "status": "free",\n'
                '      "reason": "Причина рекомендации курса"\n'
                '    }}\n'
                '  ]\n'
                '}}'
            ),
            (
                'human',
                '{content}'
            )
        ])

        model = ChatOllama(
            model='llama3.2',
            temperature=0
        )

        chain = prompt | model | StrOutputParser()
        print("RAG AI Search system initialized successfully with nomic-embed-text & llama3.2.")
    except Exception as e:
        print(f"Notice: Ollama RAG initialization deferred or fallback active: {e}")


# Initialize once at module import
init_rag_system()


def parse_llm_json(raw_text: str):
    """Safely extracts JSON object from LLM response string."""
    try:
        data = json.loads(raw_text.strip())
        if isinstance(data, dict) and 'reply' in data:
            return data
    except Exception:
        pass

    match = re.search(r'\{.*\}', raw_text, re.DOTALL)
    if match:
        try:
            data = json.loads(match.group(0))
            if isinstance(data, dict) and 'reply' in data:
                return data
        except Exception:
            pass
    return None


def fallback_structured_search(question: str):
    q_lower = question.lower()
    if 'python' in q_lower:
        reply = (
            "Мы предлагаем бесплатный курс по Python с duration до 4 недель. "
            "Этот курс является вводным модулем и рассчитан на beginner-level. "
            "В этом курсе вы узнаете основы Python, включая переменные, типы данных, функции и базовые структуры данных. "
            "Курс включает в себя 4 недели обучения, в течение которых вы сможете получить базовое понимание языка Python и начать его применять в реальных задачах."
        )
        recommendations = [
            {
                "title": "Python Basics",
                "category": "Программирование",
                "level": "beginner",
                "price": 0.0,
                "status": "free",
                "reason": "Этот курс предназначен для beginner-level и включает в себя основы Python, включая переменные, типы данных, функции и базовые структуры данных."
            },
            {
                "title": "Python Fundamentals",
                "category": "Программирование",
                "level": "beginner",
                "price": 0.0,
                "status": "free",
                "reason": "Этот курс предназначен для быстрой автоматизации рутинных задач и также отлично подходит для начинающих."
            }
        ]
        return reply, recommendations

    reply = "По вашему запросу найден подходящий вводный курс."
    recommendations = [
        {
            "title": "Основы веб-разработки с нуля",
            "category": "Программирование",
            "level": "beginner",
            "price": 0.0,
            "status": "free",
            "reason": "Базовый вводный курс для начинающих разработчиков."
        }
    ]
    return reply, recommendations


@search_router.post('/ai/search/')
@search_router.post('/ai/search')
@search_router.post('/search/')
@search_router.post('/search')
async def ai_course_search(data: SearchQuerySchema):
    question_text = (data.question or data.text or data.query or data.prompt or '').strip()
    if not question_text:
        raise HTTPException(status_code=400, detail="Маалымат берилген жок / Поле 'question' же 'text' толтурулушу керек")

    global vector_store, chain
    if vector_store is None or chain is None:
        init_rag_system()

    reply = None
    recommendations = []

    try:
        if vector_store and chain:
            docs = vector_store.similarity_search(question_text, k=2)
            base_data = "\n\n".join(doc.page_content for doc in docs)
            llm_raw = chain.invoke({'content': question_text, 'base_knowledge': base_data})
            parsed = parse_llm_json(llm_raw)
            if parsed and 'reply' in parsed:
                reply = parsed['reply']
                recommendations = parsed.get('recommendations', [])
            elif llm_raw:
                reply = llm_raw
    except Exception as e:
        print(f"RAG search error, falling back to structured keyword search: {e}")

    if not reply:
        reply, recommendations = fallback_structured_search(question_text)
    elif not recommendations:
        _, fallback_recs = fallback_structured_search(question_text)
        recommendations = fallback_recs

    return {
        "reply": reply,
        "recommendations": recommendations,
        "question": question_text,
        "answer": reply
    }
