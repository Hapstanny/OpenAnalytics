from langchain.agents import create_spark_sql_agent,AgentType
from langchain.agents.agent_toolkits import SparkSQLToolkit
from langchain.chat_models import ChatOpenAI,AzureChatOpenAI
from langchain.llms import AzureOpenAI
from langchain.utilities.spark_sql import SparkSQL
from databricks.connect import DatabricksSession
from pyspark.sql import SparkSession
from databricks.sdk.core import Config
from databricks.connect import DatabricksSession
from langchain.memory import ConversationBufferMemory
from cfg import Cfg
import streamlit as st
import sys


# Define the OpenAI keys

openai_api_version=Cfg.openaiCfg['openai_api_version']
openai_api_key=Cfg.openaiCfg["openai_api_key"]
openai_api_base=Cfg.openaiCfg["openai_api_base"]


#Creating Spark Session with Databricks token

spark_session = DatabricksSession.builder.remote(
    host=Cfg.databricksCfg["host"],
    cluster_id=Cfg.databricksCfg["cluster_id"],
    token=Cfg.databricksCfg["token"],
    ).getOrCreate()


# Define streamlit app page

st.title('Databricks Big Data Analytics with AzureOpenAI')
st.markdown("""
    This app builts on Spark SQL agent running on AzureOpenAI \n
    It uses LLM model to query and analyse Delta lake in Databricks \n
    ### Select catalog & database to analyse Delta lake in databricks
    """)


# Get list of catalogs and databases from Databricks

catalog_df = spark_session.sql("show catalogs")
catalog_df.show()

catalog=st.sidebar.selectbox('Select Catalog', catalog_df.toPandas()["catalog"].tolist())

databaseName=spark_session.sql("show databases in " + catalog).toPandas()["databaseName"].tolist()
databaseName.append("None Selected")
print(databaseName)

schema=st.sidebar.selectbox('Select Database', databaseName)
Url="sc://"+ Cfg.databricksCfg["host"] + ":" + Cfg.databricksCfg["port"] + "/;token=" + Cfg.databricksCfg["token"] + ";x-databricks-cluster-id=" + Cfg.databricksCfg["cluster_id"]

# Create SpqrkSQL session with remote URI

if schema!="None Selected":
    spark_sql=SparkSQL.from_uri(database_uri=Url,catalog=catalog,schema=schema)
else:
    print("None Selected")
    spark_sql=SparkSQL.from_uri(database_uri=Url,catalog=catalog)  


# Get list of models from AzureOpenAI 

model=st.radio('Select Model', ["text-davinci-003","gpt-35-turbo","gpt-35-turbo-16K"], index=0)

if model=='gpt-35-turbo':
    deployment_name="completion_gpt35"
elif model=='text-davinci-003':
    deployment_name="completion_davinci003"
elif model=='gpt-35-turbo-16K':
    deployment_name="completion_gpt35_16k"


# Define max tokens for AzureOpenAI
max_tokens=st.slider('Max Tokens', min_value=750, max_value=16000, value=3000, step=10)
    
# Create AzureOpenAI model

if deployment_name=="completion_davinci003":
    llm = AzureOpenAI(deployment_name=deployment_name, openai_api_version=openai_api_version, openai_api_key=openai_api_key, openai_api_base=openai_api_base,temperature=0)
else:
    llm = AzureChatOpenAI(deployment_name=deployment_name, openai_api_version=openai_api_version, openai_api_key=openai_api_key, openai_api_base=openai_api_base,temperature=.7,max_tokens=max_tokens)

# Create spark sql agent

toolkit = SparkSQLToolkit(db=spark_sql, llm=llm)
agent_executor = create_spark_sql_agent(
    llm=llm,
    prefix=Cfg.promptPrefix,
    format_instructions=Cfg.promptIns,
    toolkit=toolkit,
    verbose=True,
    return_intermediate_steps=True,
)

# Print the prompt template
#print(agent_executor.agent.llm_chain.prompt.template)

query=st.text_area("Enter your Databricks Query", height=100, max_chars=500, key="query")
print(query)

button=st.button("Run Query")

# Run the LLM agent
if query=="" and button==True:
    print("Processing with default query: show all tables")
    st.write("Non Selected, Processing with default query: show all tables in selected database")
    query="show all tables in selected database"
    st.write("Final Obervation:")
    st.write(agent_executor.run(query))
    #response=agent_executor({"input":query})
    #print(response)
    #st.write(response["intermediate_steps"])
elif query!="" and button==True:
    print("Processing with query: " + query)
    st.write("Final Obervation:")
    st.write(agent_executor.run(query))
# agent_executor.run("show all tables")

