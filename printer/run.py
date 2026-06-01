import streamlit as st

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
    # 设置文件地址
    file_path = '/Users/openclaw/Documents/AI/咕泡第五期课件资料/02+03.第二章&第三章课件资料/5.【RAG检索增强生成技术实战】/RAG/曲面打印机说明书.txt'
    # 展示
    interactive(file_path)
