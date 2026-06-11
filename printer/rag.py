import os

import streamlit as st
from langchain_community.document_loaders import TextLoader
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableParallel, RunnablePassthrough
from langchain_openai import ChatOpenAI
from langchain_text_splitters import RecursiveCharacterTextSplitter

# 如果需要使用OpenAI密钥对 请解除这部分注释 并将42-47行部分阿里云的llm和embedding加载部分注释掉
# load_dotenv('/Users/kane/PycharmProjects/rag_demo/.env')
# openai_endpoint: str = os.getenv('OPENAI_ENDPOINT')
# openai_api_key: str = os.getenv('OPENAI_API_KEY')
# openai_api_version: str = os.getenv('OPENAI_API_VERSION')
# openai_deployment: str = os.getenv('OPENAI_DEPLOYMENT')
# embedding_deployment: str = os.getenv('EMBEDDING_DEPLOYMENT')
# embedding_api_version: str = os.getenv('EMBEDDING_API_VERSION')
# embedding_api_key: str = os.getenv('EMBEDDING_API_KEY')
# embedding_endpoint: str = os.getenv('EMBEDDING_ENDPOINT')
# llm = ChatOpenAI(
#     deployment=openai_deployment,
#     openai_api_version=openai_api_version,
#     endpoint=openai_endpoint,
#     api_key=openai_api_key,
# )
# embeddings = OpenAIEmbeddings(
#     openai_api_version=embedding_api_version,
#     base_url=embedding_endpoint,
#     api_key=embedding_api_key,
#     deployment=embedding_deployment
#  )


#配置AI密钥&模型
embeddings = DashScopeEmbeddings(
    model="text-embedding-v2",
    dashscope_api_key="sk-94af811236f74c63bc0b2193c4c295b9")

llm = ChatOpenAI(base_url='https://dashscope.aliyuncs.com/compatible-mode/v1',
                 api_key="sk-94af811236f74c63bc0b2193c4c295b9",
                 model="qwen-plus", temperature=0.7)

#文本切块 方便AI检索
def text_chunk(file_path):
    # 加载指定路径的文本文件
    loader = TextLoader(file_path, encoding='utf-8')
    docs = loader.load()
    print(docs[0].metadata)

    # 把文本分割成 500 字一组的切片
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50  # 设置文本重叠
    )
    chunks = text_splitter.split_documents(docs)
    return chunks

#切块 → 向量库 把切片变成向量，存入FAISS本地向量库
def chunk2vector(docs, embeddings):
    # new_client = chromadb.EphemeralClient()
    vector = FAISS.from_documents(
        documents=docs,  # 设置保存的文档
        embedding=embeddings  # 设置 embedding model
    )
    return vector


#构建问答链
#构建 RAG 流程：
#用户问题 → 检索相关文档
#把问题 + 文档 → 给大模型
#模型生成答案
#返回答案
def llm_chain(vector):
    template = """You are an assistant for question-answering tasks. Use the following pieces of retrieved context to answer the question. If you don't know the answer, just say that you don't know. 

    Question: {question} 

    Context: {context} 

    Answer:"""
    prompt = ChatPromptTemplate.from_template(template)
    retriever = vector.as_retriever()
    chain = (
            RunnableParallel({"context": retriever, "question": RunnablePassthrough()})
            | prompt
            | llm
            | StrOutputParser()
    )
    return chain


def llm_an(file_path, question):
    # 避免question输入为空导致报错
    if not question:
        question = "hello"
    try:
        docs = text_chunk(file_path)
        vetcor = chunk2vector(docs, embeddings)
        chain = llm_chain(vetcor)
        answer = chain.invoke(question)
        return answer
    except Exception as e:
        error_msg = f"抱歉，AI服务暂时无法访问。错误信息：{str(e)}\n\n请检查：\n1. API Key 是否有效\n2. 账户是否欠费\n3. 模型是否有访问权限（建议使用 qwen-plus、qwen-turbo、text-embedding-v3 等模型）"
        return error_msg

#Streamlit 网页界面
def interactive(file_path):
    st.title("RAG")
    # st.sidebar.header("")

    with st.expander("RAG知识库"):
        # 创建一个问题
        question_title = "您的问题是？"

        # 创建问答框，并获取用户输入
        usr_question = st.text_input(question_title)

        # 获取答案
        usr_ans = llm_an(file_path, usr_question)

        # 显示用户输入的内容
        st.write(f' {usr_ans}')


#运行入口（启动项目）
#读取打印机说明书.txt
#切成 500 字小切片
#切片变成向量
#存入本地 FAISS 向量库
#启动 Streamlit 网页
#你输入问题
#系统去向量库检索相关内容
#把问题 + 内容丢给通义千问大模型
#模型生成答案
#答案显示在网页上
if __name__ == "__main__":
    # 获取项目根目录
    PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # 设置文件地址 - 相对于项目根目录
    file_path = os.path.join(PROJECT_ROOT, "printer", "曲面打印机说明书.txt")
    
    if not os.path.exists(file_path):
        st.error(f"文件未找到: {file_path}")
    else:
        # 展示
        interactive(file_path)
