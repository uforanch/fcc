import json 
from pathlib import Path

with open(Path.cwd() / 'source-python' / "vector_database-token.json", 'r') as f:
    vector_database_token = json.load(f)

ASTRA_DB_SECURE_BUNDLE_PATH= f"{Path.cwd() / 'source-python' / 'secure-connect-vector-database.zip'}" 
#os.join(os.getcwd(),'secure-connect-vector-database')
ASTRA_DB_APPLICATION_TOKEN =vector_database_token['token']
ASTRA_CLIENT_ID=vector_database_token['clientId']

ASTRA_DB_KEYSPACE = "search"
ASTRA_DB_CLIENT_SECRET = vector_database_token['secret']

OPEN_API_KEY="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"

from langchain.vectorstores.cassandra import Cassandra
from langchain.indexes.vectorstore import VectorStoreIndexWrapper
from langchain.llms.openai import OpenAI
from langchain.embeddings import OpenAIEmbeddings

from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider

from datasets import load_dataset

cloud_config = {'secure_connect_bundle':  ASTRA_DB_SECURE_BUNDLE_PATH}
auth_provider = PlainTextAuthProvider(ASTRA_CLIENT_ID, ASTRA_DB_CLIENT_SECRET)
cluster = Cluster(cloud=cloud_config, auth_provider=auth_provider)
astraSession = cluster.connect()

llm = OpenAI(openai_api_key=OPEN_API_KEY)
myEmbedding = OpenAIEmbeddings(openai_api_key=OPEN_API_KEY)

myCassandraVStore = Cassandra(
    embedding=myEmbedding,
    session=astraSession,
    keyspace=ASTRA_DB_KEYSPACE,
    table_name="qa_mini_demo"
)

print("Loading data from huggingface")
myDataset = load_dataset("Biddls/Onion_News", split="train")
headlines = myDataset["text"][:50]

print("\nGenerating embeddings and storing in AstraDB")
myCassandraVStore.add_texts(headlines)

print("Inserted %i headlines.\n" % len(headlines))

vectorIndex = VectorStoreIndexWrapper(vectorstore=myCassandraVStore)

first_question=True
while True:
    if first_question:
        query_text=input("\nEnter your question or type quite to exit:")
        first_question = False
    else:
        query_text=input("\nWhat's your next question or type quit to exit:")
    if query_text.lower() == 'quit':
        break 

    print("QUESTION: \"%s\""% query_text)
    answer = vectorIndex.query(query_text, llm=llm).strip()
    print("ANSWER: \"%s\""% answer)

    print("DOCUMENTS BY REFERENCE:")
    for doc, score in myCassandraVStore.similarity_search_with_score(query_text, k=4):
        print("  %0.4f \"%s ...\"" % (score, doc.page_content[:60]))
        
