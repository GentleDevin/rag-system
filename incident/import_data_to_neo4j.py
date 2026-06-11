import pandas as pd
import py2neo
import os

# 获取项目根目录
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_FILE = os.path.join(PROJECT_ROOT, "incident", "data-v11.xlsx")

graph = py2neo.Graph("bolt://localhost:7687", auth=("neo4j", "neo4j123"))

if __name__ == '__main__':
    # clean the database
    #graph.run("MATCH (n) DETACH DELETE n")

    # import data
    if not os.path.exists(DATA_FILE):
        print(f"Error: Data file not found at {DATA_FILE}")
        print("Please place the data-v11.xlsx file in the incident directory.")
        exit(1)
    df = pd.read_excel(DATA_FILE)
    # 'Time', 'System', 'Incident', 'Account', 'Level', 'Reason', 'Loss'
    for index,row in df.iterrows():
        cql = f"merge (t:Time {{name:'{row['Time']}'}})"
        cql += f"merge (s:System {{name:'{row['System']}'}})"
        cql += f"merge (i:Incident {{name:'{row['Incident']}'}})"
        cql += f"merge (a:Account {{name:'{row['Account']}'}})"
        cql += f"merge (le:Level {{name:'{row['Level']}'}})"
        cql += f"merge (r:Reason {{name:'{row['Reason']}'}})"
        cql += f"merge (lo:Loss {{name:'{row['Loss']}'}})"

        cql += "merge (i)-[:Time]->(t)"
        cql += "merge (i)-[:System]->(s)"
        cql += "merge (i)-[:Account]->(a)"
        cql += "merge (i)-[:Level]->(le)"
        cql += "merge (i)-[:Reason]->(r)"
        cql += "merge (i)-[:Loss]->(lo)"

        graph.run(cql)
        print("Importing data to Neo4j: ", index+1, " / ", len(df))