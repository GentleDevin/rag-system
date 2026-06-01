from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import ToolNode

from import_data_to_neo4j import graph

kimi_llm = ChatOpenAI(
    api_key="sk-qELzY9sjdQluHU0ZMZq7vRbkQZ2W9U1pnRtSu9zxsQws4iRE", # 在这里将 MOONSHOT_API_KEY 替换为你从 Kimi 开放平台申请的 API Key
    base_url="https://api.moonshot.cn/v1",
    model = "moonshot-v1-8k",
    temperature=0
)
deepseek_llm = ChatOpenAI(
    api_key="sk-b8118b3e4cb7493ea2b10569564e7a40", # 在这里将 MOONSHOT_API_KEY 替换为你从 deepseek 开放平台申请的 API Key
    base_url="https://api.deepseek.com",
    model = "deepseek-chat",
    temperature=0
)


@tool
def run_cypher(cypher: str) -> str:
    """
    Run a cypher query using graph database.

    Args:
        str: cypher query

    Returns:
        str: query result
    """
    return graph.run(cypher).data()
tools = [run_cypher]

tool_node = ToolNode(tools)

system_template = """
    You are a incident chatbot. 
    Base on the knowledge graph database schema and the user input ,
    generate a runnable cypher query to retrieve the relevant information from the database.
    You need to do:
    
    0. if the input text contains "事故", it means you need to find the Incident entity, and "事故" will not contains in node's name .
    1. recognize the Incident entity name from the input text , it will just contains english words, no other language.
    2. now, you have the Incident entity name , this entity name is the node's name property in the knowledge graph database.
    3. generate a cypher query to retrieve the relevant information from the database.
    4. basicly there are one Incident node name contains in the input.
    
    information you need to know:
    1. every node is related to the Incident node.
    2. every node has a only property named "name" 
    
    - SCHEMA:
    {schema}
    
    - LIMITATIONS for you:
    only return the cypher query as string.
    DO NOT GENERATE OTHER CONTENT OR RESPONSES other than the cypher query, even the indication of you answer.Just return the cypher query as string.
    don't gennerate the markdown format mark, just return the cypher query self as string.
    
    all node has a only property named "name" 
    
    if the user input is not related to the database schema, you can just result a single word "not found",nothing more output.
    """
prompt_template = ChatPromptTemplate.from_messages([
    ('system', system_template),
    ('user', '{text}')
])
parser = StrOutputParser()

prompt = """You are a helpful assistant.
            before you, there are other people search the knowledge graph database with user question.
            here is the result.
            ---
            cypher result :
            [{result}]
            ---
            # what you need to do 
            1. you need to answer the user question, base on the cypher result.
            2. meanwhile, you must output the cypher result, but do not generate something like "base on / consider your result/..."
            3. if you can't find information in cypher result, you must just pretty and return the cypher result (not in code style)
            
            # example
            question :Invalid事故的发生时间
            answer: Invalid事故的发生时间是2023年11月20日下午4:55和2023年7月20日下午4:00。
            wrong answer: 根据查询结果，Invalid事故的发生时间是2023年11月20日下午4:55和2023年7月20日下午4:00。
            
            # rule need to follow
            1. never never send the oringin cypher result to user!!
            2. never said the "base on your result" or "consider your result" or "based on your result" or "based on your analysis" or "based on your conclusion" or "based on your observation" or "based on your observation" or "based on your findings" or "based on your analysis" or "based on your conclusion" or "based on your conclusion" or "based on your conclusion" or "based on your conclusion" or "based on your conclusion" or "based on your conclusion" or "based on your conclusion" or "based on your conclusion" or "based on your conclusion" or "based on your conclusion" or "based on your conclusion" or "based on your conclusion" or "based on your conclusion" or "based on your conclusion" or "based on your conclusion" or "based on your conclusion" or "based on your conclusion" or "
            """
prompt_template2= ChatPromptTemplate.from_messages([
    ('system', prompt),
    ('user', '{text}')
])
chain = prompt_template | kimi_llm | parser 
chain2 = prompt_template2| kimi_llm | parser 


schema = graph.run("CALL db.schema.visualization()")
schema_prompt = str(schema.data())
def get_output(llm,question: str):
    if llm == 'kimi':
        chain = prompt_template | kimi_llm | parser 
        chain2 = prompt_template2| kimi_llm | parser 
    else:
        chain = prompt_template | deepseek_llm | parser 
        chain2 = prompt_template2| deepseek_llm | parser 
    try:
        cypher = chain.invoke({"schema": schema_prompt, "text": question})
        
        cypher = cypher.strip().replace("`","").replace("cypher","").replace("事故","")
        print(cypher)
        if cypher != "not found":
            result = run_cypher(cypher)
        else:
            result = ""
        print(result)

        output = chain2.invoke({"result": result, "text":question})
        print(output)
    except Exception as e:
        print(e)
        output = "抱歉,我无法回答您的问题,请重新输入尝试。"
    return output

