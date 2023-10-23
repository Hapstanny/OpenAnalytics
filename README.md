# OpenAnalytics

# This app builts on Spark SQL agent running on AzureOpenAI. It uses LLM model to query and analyse Delta lake in Databricks.


## Setup Credentials -

**Azure OpenAI Credentials** - First [Create Azure OpenAI Service](https://learn.microsoft.com/en-us/azure/ai-services/openai/how-to/create-resource?pivots=web-portal), if it isn't already available. Otherwise, you can go to https://portal.azure.com, find your Azure OpenAI under "Resource Management" -> "Keys and Endpoints" look for one of the "Keys" values.

**Databricks Token** - You can create Personal Databricks Token from User Settings within your Azure Databricks workspace.  Refer [Generate Databricks personal access token](https://learn.microsoft.com/en-us/azure/databricks/dev-tools/auth#--azure-databricks-personal-access-tokens-for-workspace-users) for details. Get Cluster_id via CLI or get it from respective compute cluster tags in portal.

# Define the OpenAI keys

	openai_api_version=Cfg.openaiCfg['openai_api_version']
	openai_api_key=Cfg.openaiCfg["openai_api_key"]
	openai_api_base=Cfg.openaiCfg["openai_api_base"]


# Creating Spark Session with Databricks token

	spark_session = DatabricksSession.builder.remote(
	    host=Cfg.databricksCfg["host"],
	    cluster_id=Cfg.databricksCfg["cluster_id"],
	    token=Cfg.databricksCfg["token"],
	    ).getOrCreate()

# Install Required Packages-  
Below are the key packages required for this app.  You can do pip install them in your environment if these aren't already available.

	from langchain.agents import create_spark_sql_agent,AgentType
	from langchain.agents.agent_toolkits import SparkSQLToolkit
	from langchain.chat_models import ChatOpenAI,AzureChatOpenAI
	from langchain.llms import AzureOpenAI
	from langchain.utilities.spark_sql import SparkSQL
	from databricks.connect import DatabricksSession

# Create Spark Session in Databricks - 
Invoke remote spark session by passing Databricks cluster URL with host, token and cluster-id details.
 
	Url="sc://"+ Cfg.databricksCfg["host"] + ":" + Cfg.databricksCfg["port"] + "/;token=" + Cfg.databricksCfg["token"] + ";x-databricks-cluster-id=" + Cfg.databricksCfg["cluster_id"]
	
	spark_sql=SparkSQL.from_uri(database_uri=Url,catalog=catalog,schema=schema)

# Create Azure OpenAI Object - 
You can get model deployment details (Deployment Name) from [Azure OpenAI Studio](https://oai.azure.com/). Refer below for details.

[Deploy Azure OpenAI Model](https://learn.microsoft.com/en-us/azure/ai-services/openai/how-to/create-resource?pivots=web-portal#deploy-a-model)

	llm = AzureChatOpenAI(deployment_name=deployment_name, openai_api_version=openai_api_version, openai_api_key=openai_api_key, openai_api_base=openai_api_base,temperature=.7, max_tokens=max_tokens)

Spark Sql Agent - Refer below code to create spark sql agent. It has been parameterized with custom prompt prefix and instructions.

# Use prefix and format_instructions to pass the custom prompt.

	toolkit = SparkSQLToolkit(db=spark_sql, llm=llm)
	agent_executor = create_spark_sql_agent(
	    llm=llm,
	    prefix=Cfg.promptPrefix,
	    format_instructions=Cfg.promptIns,
	    toolkit=toolkit,
	    verbose=True,
	    return_intermediate_steps=True,
	)

# Run the Agent - 
Provide user query as input to the agent. Below code has used  [streamlit](https://streamlit.io/) package to pass this info to agent.

	query=st.text_area("Enter your Databricks Query", height=100, max_chars=500, key="query")
	
	agent_executor.run(query)

# Output -

## DDL Operation

![Alt text](/images/image-1.png)

# Example 2 - 

![Alt text](/images/image-1.png)

# Example 3 - 

![Alt text](/images/image-2.png)
