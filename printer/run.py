import streamlit as st
import os

from rag import llm_an


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
