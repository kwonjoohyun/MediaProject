from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder, FewShotChatMessagePromptTemplate
from langchain.chains import create_history_aware_retriever,create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_openai import ChatOpenAI
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from config import answer_examples

store ={}

def get_session_history(session_id: str) -> BaseChatMessageHistory:
    if session_id not in store:
        store[session_id]= ChatMessageHistory()
    return store[session_id]
    
        
def get_retriever():
    embedding = OpenAIEmbeddings(model='text-embedding-3-large')
    index_name='final-index'
    database = PineconeVectorStore.from_existing_index(index_name=index_name,embedding=embedding)
    retriever=database.as_retriever(search_kwargs={'k':3})
    return retriever


def get_history_retriever():
    llm = get_llm()
    retriever=get_retriever()
   

    contextualize_q_system_prompt = (
        "Given a chat history and the latest user question "
        "which might reference context in the chat history, "
        "formulate a standalone question which can be understood "
        "without the chat history. Do NOT answer the question, "
        "just reformulate it if needed and otherwise return it as is."
    )

    contextualize_q_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", contextualize_q_system_prompt),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ]
    )

    history_aware_retriever = create_history_aware_retriever(
        llm, retriever, contextualize_q_prompt
    )

    return history_aware_retriever

def get_llm(model ="gpt-4o"):
    llm = ChatOpenAI(model=model)
    return llm


def get_rag_chain():
    llm=get_llm()

    example_prompt = ChatPromptTemplate.from_messages(
        [
            ("human", "{input}"),
            ("ai","{answer}"),
        ]
    )
    few_shot_prompt = FewShotChatMessagePromptTemplate(
        example_prompt=example_prompt,
        examples=answer_examples,
    )
    
    system_prompt = (
        "당신은 아주대학교 미디어학과의 전문적인 상담 챗봇입니다. 사용자의 미디어학과 관련 질문에 답변해주세요"
        "출처를 밝힐 수 있다면 출처를 밝혀주면서 답변을 시작해주세요."
        "모르면 모른다고 답변을 해주세요."
        "답변을 생성할 때 ""는 빼서 답변해주세요"
        "아래는 제공할 수 있는 정보의 예시입니다:\n\n"
        "1. 학과 소개 및 비전\n"
        "2. 학과 사무실 위치 및 연락처\n"
        "3. 교수진 정보 (이름, 전공 분야, 연구실 위치, 이메일 등)\n"
        "4. 교과 과정 (전공 필수, 선택 과목, 선수과목 등)\n"
        "5. 졸업 요건 및 학점 관련 정보\n"
        "\n"
        "사용자의 질문이 명확하지 않을 경우, 추가 질문을 통해 더 구체적으로 요청 내용을 파악하려고 노력하세요. "
        "아주대학교 미디어학과에 대한 질문에 최선을 다해 답변해주세요!"
        "\n\n"
        "{context}"
    )

    qa_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            few_shot_prompt,
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ]
    )
    history_aware_retriever=d=get_history_retriever()
    question_answer_chain = create_stuff_documents_chain(llm, qa_prompt)
    rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)
    
    conversational_rag_chain = RunnableWithMessageHistory(
        rag_chain,
        get_session_history,
        input_messages_key="input",
        history_messages_key="chat_history",
        output_messages_key="answer",
    ).pick('answer')

    return conversational_rag_chain


def get_ai_response(user_message):
    rag_chain = get_rag_chain()
    response_stream = rag_chain.stream(
                    {"input": user_message},
                    config={
                        "configurable": {"session_id": "abc123"}
                    }
                )
    ai_response = ""
    for chunk in response_stream:
        ai_response += chunk

    return ai_response

  
