from langchain_agent.imports import *
from langchain_agent.usefulmethod import *
from langchain_agent.prompts_set import *
from langchain_agent.json_save import *
# Set the task
class MyTask:
    
    def __init__(
        self, 
        llm:BaseLanguageModel, 
        retriever,
        llm_model_type :int=1,
    ):
        """
        Args:
        llm (BaseLanguageModel):大语言模型
        vectorstore 为数据库
        retriever (BaseRetriever): 检索
        """
        self.llm = llm
        self.retriever = retriever
        self.llm_model_type = llm_model_type
    
    def tool_query(
        self
    ):
        return self.retriever
    
    # 查询向量存储的函数
    def query(
        self,
        question: str,                                          # 输入的问题字符串
    ):
        """Query the vectorstore.
            查询向量存储的函数
            基础的知识摘要，直接从数据库里面获取与输入内容相关的数据
        """                                               
        documents=self.retriever.get_relevant_documents(query = question)
        # 使用列表推导式提取所有的 page_content
        page_contents = [doc.page_content for doc in documents]

        # 将所有的 page_content 合并成单一的字符串
        full_content = "\n".join(page_contents)
        
        # res = history_Opt().message_Optimization(message=full_content,prompt_type=1) 
        return full_content
        # return self.retriever.get_relevant_documents(question)

    # 查询向量存储并返回数据源的函数
    def query_with_sources(
        self,
        question: str
    ) -> dict:
        """
        Query the vectorstore and get back sources.
        基础的知识摘要，直接从数据库里面获取与输入内容相关的数据源的位置
        """
        chain = RetrievalQAWithSourcesChain.from_chain_type(
            llm=self.llm,
            retriever=self.retriever
        )
        return chain({chain.question_key: question})
 
# Vectorize the contents of the path
class KnownLedge2Vector():
    """
    用于将Pdatasetdir路径下的文件向量化并返回一个向量存储
    使用格式：
    vector_store = KnownLedge2Vector(
        dbpath=dbPath,
        datasetdir=sourcePath,
        model_name=LLM_TYpe
        ).init_vector_store()
    """
    def __init__(
            self,
            dbpath: Union[str, None] = "", 
            datasetdir: Union[str, None] = "",
            model_name: int = 1,
            chunk_size:int = 500,
            chunk_overlap:int = 50
        ) -> None:  
        """
        Args:
        dbpath (str):持久化向量数据库的 保存地址路径
        datasetdir (str):要加载的资源路径
        model_name (int) :选择模型进行资料向量化 1 openai 2 wenxin 3 miniamax 
        chunk_size(int) :划分文本的大小
        """
        self.dbpath=dbpath
        self.datasetdir=datasetdir
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        if model_name == 1:  # 如果没有提供模型名称
            # 创建一个 OpenAIEmbeddings 对象
            self.embeddings = OpenAIEmbeddings()  
        elif model_name == 2:
            # 创建一个 HuggingFaceEmbeddings 对象
            # self.embeddings = HuggingFaceEmbeddings()
            raise ValueError("向量错误,model_name的值请在1/3之间选择")
        elif model_name == 3:
            # 创建一个 HuggingFaceEmbeddings 对象
            self.embeddings = MiniMaxEmbeddings()
        else:
            raise ValueError("向量错误,model_name的值请在1/3之间选择")
            
    
    def _load_file(self, filename):
        """
        分析并加载数据
        """
        # 判断文件类型
        if filename.lower().endswith(".pdf"):  # 如果文件是 PDF 格式
            loader = UnstructuredFileLoader(filename)   # 使用 UnstructuredFileLoader 加载器来加载 PDF 文件
            # text_splitor = CharacterTextSplitter()      # 使用 CharacterTextSplitter 来分割文件中的文本
            text_splitor =RecursiveCharacterTextSplitter(
                chunk_size = self.chunk_size,
                chunk_overlap = self.chunk_overlap
            )
            docs = loader.load_and_split(text_splitor)  # 加载文件并进行文本分割
        else:          # 如果文件不是 PDF 格式
            loader = UnstructuredFileLoader(filename, mode="elements")  # 使用 UnstructuredFileLoader 加载器以元素模式加载文件
            # text_splitor = CharacterTextSplitter()      # 使用 CharacterTextSplitter 来分割文件中的文本
            text_splitor =RecursiveCharacterTextSplitter(
                chunk_size = self.chunk_size,
                chunk_overlap = self.chunk_overlap
            )
            docs = loader.load_and_split(text_splitor)  # 加载文件并进行文本分割
        return docs    # 返回处理后的文件数据
    
    def init_vector_store(self):
        """
        向量化数据并存储
        """
        persist_dir = os.path.join(self.dbpath, ".vectordb")  # 持久化向量数据库的地址
        print("向量数据库持久化地址: ", persist_dir)              # 打印持久化地址
    
        # 如果持久化地址存在
        if os.path.exists(persist_dir):  
            # 从本地持久化文件中加载
            print("从本地向量加载数据...")
            # 使用 Chroma 加载持久化的向量数据
            vector_store = Chroma(persist_directory=persist_dir, embedding_function=self.embeddings)  
            #打印向量数据库中的文档数量
            print(vector_store._collection.count())
        # 如果持久化地址不存在
        else:      
            # 加载知识库
            documents = self.load_knownlege()  
            # 使用 Chroma 从文档中创建向量存储
            vector_store = Chroma.from_documents(documents=documents, 
                                                embedding=self.embeddings,
                                                persist_directory=persist_dir)  
            # vector_store = FAISS.from_documents(documents=documents, 
            #                                     embedding=self.embeddings,
            #                                     persist_directory=persist_dir)  
            vector_store.persist()      # 持久化向量存储
        return vector_store             # 返回向量存储
        
    def SelfqueryRetriever(
            self,
            task:MyTask,
            retriever
        )->SelfQueryRetriever:
        """
        创建一个自定义的retriever
        使用LLM过滤
        """
        #定义元数据的过滤条件
        metadata_field_info = [
            AttributeInfo(
                name="source",
                description="The lecture the chunk is from, should be one of `docs/cs229_lectures/MachineLearning-Lecture01.pdf`, `docs/cs229_lectures/MachineLearning-Lecture02.pdf`, or `docs/cs229_lectures/MachineLearning-Lecture03.pdf`",
                type="string",
            ),
            AttributeInfo(
                name="page",
                description="The page from the lecture",
                type="integer",
            ),
        ]
        
        # document_contents: The contents of the document to be queried.
        document_content_description = "Lecture notes"
        # 创建SelfQueryRetriever
        retriever = SelfQueryRetriever.from_llm(
            task.llm,
            retriever,
            document_content_description,
            metadata_field_info,
            verbose=True
        )
        return retriever

    def load_knownlege(self):
        """ 
        加载目录下的所有文件并且将该路径下的文件转换成向量数据

        datasetdir 资源路径
        """
        docments = []         # 初始化一个空列表来存储文档

        # 遍历 DATASETS_DIR 目录下的所有文件
        for root, _, files in os.walk(self.datasetdir, topdown=False):
            for file in files:
                filename = os.path.join(root, file)      # 获取文件的完整路径
                print("filename",filename)
                docs = self._load_file(filename)         # 加载文件中的文档

                # 更新 metadata 数据
                new_docs = []             # 初始化一个空列表来存储新文档
                for doc in docs:
                    # 更新文档的 metadata，将 "source" 字段的值替换为不包含 DATASETS_DIR 的相对路径
                    doc.metadata = {"source": doc.metadata["source"].replace(self.datasetdir, "")} 
                    print("文档2向量初始化中, 请稍等...", doc.metadata)  # 打印正在初始化的文档的 metadata
                    new_docs.append(doc)  # 将文档添加到新文档列表

                docments += new_docs      # 将新文档列表添加到总文档列表

        return docments      # 返回所有文档的列表
    
class Pdf_to_Vector():
    def test(self,):
        pass
   
class Redis_Create():
    """
    创建redis数据库
    使用格式：
    redis = Redis_Create(
        url=url,
        ttl=ttl,
        session_id=session_id
        ).get_redis_db()
    """
    def __init__(
            self,
            url: str='redis://localhost:6379/0', 
            ttl: int = 600,
            session_id: str="my-session"
        ) -> None:  
        """
        Args:
        url (str):这是Redis服务器的连接字符串
        ttl (int):这是时间(以秒为单位),指定了消息在Redis中的存活时间（Time To Live）
        session_id (str) :区分不同用户或会话的唯一标识符
        """
        self.url = url
        self.ttl = ttl
        self.session_id = session_id
        self.redis_db_time = RedisChatMessageHistory(
            url= url, ttl=ttl , session_id=session_id
        )
        self.llm = OpenAI(openai_api_key="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",temperature=0.7)

    def get_redis_db(self):
        return self.redis_db_time
    
    def clear_redis_data(self):
        # 清空Redis数据库
        self.redis_db_time.flushdb()
    # 方法：生成对整体事件的高度概括提示
    def summarize(self, text: str):
        """
        使用OpenAI语言模型进行总结。

        参数:
        text (str): 需要总结的文本
        """
        prompt = f"请总结以下对话内容,总结的时候要包括日期:{text}"
        print("prompt",prompt)
        res = self.llm(prompt)
        print("-----",res)
        return res

    def load_json_memory(self, filepath):
        # 遍历简化的JSON数据
        with open(filepath, 'r') as file:  # 'r' mode opens the file for reading
            file_content = json.load(file)  # Assuming the file content is in JSON format
        for entry in file_content:
            # 提取时间、用户对话和AI对话
            date = entry["time"].split("T")[0]  # 获取日期部分
            user_dialogue = entry["user"]
            ai_dialogue = entry["ai"]
            summary = f"在{date},user:{user_dialogue.strip()}AI: {ai_dialogue.strip()}"
            res = self.summarize(summary)
            self.redis_db_time.add_user_message(user_dialogue)
            self.redis_db_time.add_ai_message(res)
            print(res)
        # print(self.redis_db_time.message)
        return self.redis_db_time
            

 
class Vect_Agent:
    """
    Agent代理办法与知识库交互
    agentchain_memory 方法:已经可以使用，但是需要 prefix 参数,prefix (Literal):使用工具前的字符串输入
    效果评估 openai-85分 minimax-65分
    agentchain_office_memory 方法: 
    """
    def __init__(
            self,
            task:MyTask,
            vector_store:Chroma, 
        ) -> None:
        """
        Args:
        vector_store (Chroma):已经转换成向量的数据库
        """
        self.vector_store = vector_store
        self.llm = task.llm
        self.task = task
        self.SERPAPI_API_KEY='f4e351534232e4da8e594d7225a5961c5180fe136b7a3b308843b8a64320a718'
    
    def Commaoutput(self,qs):
        output_parser = CommaSeparatedListOutputParser()
        
        return output_parser.parse(qs)

    #可以使用且稳定
    def agentchain_memory_V2(
                self,
                prefix:Literal,
        ):
        """
        带记忆的代理(创建一个共享的llm_memory与Agent共享)
        Args:
        question (str):提问题的列表
        prefix (Literal):使用工具前的字符串输入
        """
        #2 创建template_llm
        template_llm = """ 
        you are R2-D2,You should answer as much as possible {chat_history}
        you should answer question about  :{input} "

        """
        #agent template
        Agent_prefix = prefix
        Agent_suffix = """At the start the answer Always say " I "  \
        Use the following pieces of context to answer the question at the end. \
        If you don't know the answer, just say that you don't know, don't try to make up an answer. \
        Use three sentences maximum. Keep the answer as concise as possible. \
        "
        begin!
        {chat_history}
        Question: {input}
        {agent_scratchpad}"""

        #3 创建prompt
        prompt = PromptTemplate(input_variables=["input", "chat_history"], template=template_llm)
        #4 获取记忆类 - 创建共享的记忆
        memory = ConversationBufferMemory(memory_key="chat_history")
        readonlymemory = ReadOnlySharedMemory(memory=memory)
        #5 创建LLMChain 类，并使用共享记忆
        summary_chain = LLMChain(
            llm=OpenAI(),
            prompt=prompt,
            verbose=True,
            memory=readonlymemory,  # use the read-only memory to prevent the tool from modifying the memory
        )
        #6 为Agent创建工具
        docstore=DocstoreExplorer(Wikipedia())
        tools = [
            # 向量数据库搜索
            Tool(
                name="Source_Search",
                func=self.task.query,
                description="useful for when you need to answer questions about R2-D2. Input should be a fully formed question.",
                # return_direct=True
            ),
            # 大语言模型
            Tool(
                name = "llm talk",
                func=summary_chain.run,
                description="useful for when you need to normal communication. Input should be a fully formed question.",
                return_direct=True #直接返回内容 不做修改
            ),
            # 维基百科
            Tool(
                name="wiki_Search",
                func=docstore.search,
                description="useful for when you need to When you are unable to obtain answers from the document."
            ),
        ]

        #Agent创建---------------------------------------------------------------------
        #7 agnet_prompt的创建
        agnet_prompt = ZeroShotAgent.create_prompt(
            tools,
            prefix=Agent_prefix,
            suffix=Agent_suffix,
            input_variables=["input", "chat_history", "agent_scratchpad"],
        )
        #8 agent_llm_chain 的创建
        agent_llm_chain = LLMChain(llm=OpenAI(temperature=0), prompt=agnet_prompt)
        #9 创建agent代理
        agent = ZeroShotAgent(llm_chain=agent_llm_chain, tools=tools, verbose=True)
        #10 创建agentchain代理
        agent_chain = AgentExecutor.from_agent_and_tools(
            agent=agent, tools=tools, verbose=True, memory=memory
        )
        
        return agent_chain
    
    # 可以使用且稳定
    def agentchain_memory_Redis(
                self,
                prefix:Literal,
                redis_memory:Redis_Create,
        ):
        """
        使用了Redis数据库的有记忆的代理(创建一个共享的llm_memory与Agent共享)
        Args:
        question (str):提问题的列表
        prefix (Literal):使用工具前的字符串输入
        """
        
        #2 创建template_llm
        template_llm = prefix + """
        Always use the first person when answering.
        Before your response, add an emotive description, such as [smiling], [thinking], or [surprised].
        Use the following pieces of context to answer the question at the end. \
        If you don't know the answer, you can search on the web. \
        Use three sentences maximum. Keep the answer as concise as possible. \

        {chat_history}

        you should answer question about {input}:
        """
        
        # agent template
        Agent_prefix = prefix
        Agent_suffix = """
        Always use the first person when answering.
        Before your response, add an emotive description, such as [smiling], [thinking], or [surprised].
        Use the following pieces of context to answer the question at the end. \
        If you don't know the answer, you can search on the web. \
        Use three sentences maximum. Keep the answer as concise as possible. \

        begin!
        history：{chat_history}
        Question: {input}
        """
        
        
        #3 创建prompt
        prompt = PromptTemplate(input_variables=["input", "chat_history"], template=template_llm)
        
                    
        memory = ConversationBufferMemory(
            memory_key="chat_history", chat_memory=redis_memory
        )
        readonlymemory = ReadOnlySharedMemory(memory=memory)
        #4 创建LLMChain 类，并使用共享记忆
        summary_chain = LLMChain(
            llm=self.task.llm,
            prompt=prompt,
            verbose=True,
            memory=readonlymemory,  # use the read-only memory to prevent the tool from modifying the memory
        )
        #5 为Agent创建工具
        docstore=DocstoreExplorer(Wikipedia())
        os.environ["SERPAPI_API_KEY"] = 'f4e351534232e4da8e594d7225a5961c5180fe136b7a3b308843b8a64320a718'
        # search = GoogleSearchAPIWrapper()
        tools2=load_tools(["serpapi"],self.task.llm)
        agent2 = initialize_agent(tools2, self.task.llm, agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION, max_execution_time=1,verbose=True)
        tools = [
            # 向量数据库搜索
            # Tool(
            #     name="Source_Search",
            #     func=self.task.query,
            #     description="The Source_Search tool is designed to answer queries related to NPC information and can quickly find information about specific NPCs in complex data sets. \
            #          Users can ask NPCs about their background stories, characteristics, behavior patterns or any relevant details, and the tool will extract and provide the required answers from databases or libraries through precise searches.",
            #     # return_direct=True
            # ),
            # # 维基百科
            # Tool(
            #     name="wiki_Search",
            #     func=docstore.search,
            #     description="You can use the wiki_Search tool as a supplement to obtain relevant information from Wikipedia. \
            #            Users can ask various questions about NPCs, and wiki_Search will connect to Wikipedia's extensive knowledge base, retrieving and returning the most relevant entries."
            # ),
            Tool(
                name="serpapi",
                func=agent2.run,
                description="You should search together by prefixing the question with the character's name. You can supplement this by using the serpapi tool to get relevant information from Google. \
                         Users can ask various questions about NPCs, and the most relevant entries are retrieved and returned.",
                # return_direct=True
                
            ),
            # 大语言模型
            Tool(
                name = "llm talk",
                func=summary_chain.run,
                description="llm talk工具是一个高级大语言模型交互平台。\
                    用户可以与之进行日常交流，提出各种问题或请求，如天气查询、日程安排、知识问答等。\
                        llm talk将利用其庞大的语言模型库，结合上下文理解能力，给出准确、贴切的回答或建议。\
                            它是用户获取信息、解决问题的得力助手，也是提升交互体验的重要工具。"
            )
        ]

        #Agent创建---------------------------------------------------------------------
        #6 agnet_prompt的创建
        agnet_prompt = ZeroShotAgent.create_prompt(
            tools,
            prefix=Agent_prefix,
            suffix=Agent_suffix,
            input_variables=["input", "chat_history"],
        )
        #7 agent_llm_chain 的创建
        agent_llm_chain = LLMChain(llm=self.task.llm, prompt=agnet_prompt)
        #8 创建agent代理
        agent = ZeroShotAgent(llm_chain=agent_llm_chain, tools=tools, verbose=False)
        #9 创建agentchain代理
        agent_chain = AgentExecutor.from_agent_and_tools(
            agent=agent, 
            tools=tools, 
            verbose=True, 
            memory=memory,
            handle_parsing_errors=True  # 处理解析错误并重试
        )
        
        return agent_chain
    
    # 可以使用且稳定
    def agentchain_memory_json(
                self,
                prefix:str,
        ):
        """
        使用了json保存的有记忆的代理(创建一个共享的llm_memory与Agent共享)
        question (str):提问题的列表
        prefix (Literal):使用工具前的字符串输入
        """
        
        # agent template
        Agent_prefix = prefix
        Agent_suffix = """
        用户的问题: {question}
        """
        prompt_llm = Agent_prefix+Agent_suffix
        #5 为Agent创建工具
        os.environ["SERPAPI_API_KEY"] = 'f4e351534232e4da8e594d7225a5961c5180fe136b7a3b308843b8a64320a718'
        prompt = PromptTemplate(input_variables=["input"], template=prompt_llm)
        #4 创建LLMChain 类，并使用共享记忆
        summary_chain = LLMChain(
            llm=self.task.llm,
            prompt=prompt,
            verbose=True
        )
        # search = GoogleSearchAPIWrapper()
        tools2=load_tools(["serpapi"],self.task.llm)
        agent2 = initialize_agent(tools2, self.task.llm, agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION, max_execution_time=2,verbose=True)
        tools = [
            # Tool(
            #     name = "search_state_of_union",
            #     func=self.task.query,
            #     description="Search and return files with character profiles."
            # ),
            # 大语言模型
            Tool(
                name = "llm talk",
                func=summary_chain.run,
                description="用户可以与之进行日常交流，提出各种问题或请求，如天气查询、日程安排、知识问答等。"
            ),
            Tool(
                name="serpapi",
                func=agent2.run,
                description="当你不知道该怎么回答的时候可以通过这个工具在网上搜索答案，非必要不要使用这个工具"
            )
            
        ]

        #Agent创建---------------------------------------------------------------------
        #6 agnet_prompt的创建
        agnet_prompt = ZeroShotAgent.create_prompt(
            tools,
            prefix=Agent_prefix,
            suffix=Agent_suffix,
            input_variables=["question"],
        )
        #7 agent_llm_chain 的创建
        agent_llm_chain = LLMChain(llm=self.task.llm, prompt=agnet_prompt)
        #8 创建agent代理
        agent = ZeroShotAgent(
            llm_chain=agent_llm_chain,
            tools=tools,
            verbose=False,
            stop=["\nObservation:","\n最终回答:"],  #设置停止方式
            )
        
        #9 创建agentchain代理
        agent_chain = AgentExecutor.from_agent_and_tools(
            agent=agent, 
            tools=tools, 
            verbose=True, 
            max_iterations=3,           # 最大轮数限制
            max_execution_time=2,       #最大时间限制 2s
            early_stopping_method="generate",#指定generate方法，然后对LLM进行一次最终通过以生成输出。
            handle_parsing_errors=True  # 处理解析错误并重试
        )
        
        return agent_chain
    
    #更好的jsonmemomory版本，优化的不必要的bug，角色设置可以使用这个版本
    def agentchain_memory_json_latest(
                self,
                prefix:str,
        ):
        """
        使用了json保存的有记忆的代理(创建一个共享的llm_memory与Agent共享)
        question (str):提问题的列表
        prefix (Literal):使用工具前的字符串输入
        """
        
        # agent template
        Agent_prefix = prefix
        Agent_suffix = """
        一定要用中文回答问题{question}
        """
        prompt_llm = Agent_prefix+Agent_suffix
        #5 为Agent创建工具
        os.environ["SERPAPI_API_KEY"] = 'f4e351534232e4da8e594d7225a5961c5180fe136b7a3b308843b8a64320a718'
        # prompt = ChatPromptTemplate.from_messages(
        #     [("system", prompt_llm), ("human", "{query}")]
        # )
        prompt = PromptTemplate(input_variables=["question"], template=prompt_llm)
        #4 创建LLMChain 类，并使用共享记忆
        summary_chain = LLMChain(
            llm=self.task.llm,
            prompt=prompt,
            verbose=True
        )
        # search = GoogleSearchAPIWrapper()
        search = SerpAPIWrapper()
        tools = [
            Tool(
                name = "search_state_of_union",
                func=self.task.query,
                description="Search and return files with character profiles."
            ),
            # 大语言模型
            Tool(
                name = "llm talk",
                func=summary_chain.run,
                description="用户可以与之进行日常交流，提出各种问题或请求，如天气查询、日程安排、知识问答等。"
            ),
            Tool(
                name="serpapi",
                func=search.run,
                description="当你不知道该怎么回答的时候可以通过这个工具在网上搜索答案，非必要不要使用这个工具"
            )
            
        ]

        #Agent创建---------------------------------------------------------------------
        #6 agnet_prompt的创建
        agnet_prompt = ZeroShotAgent.create_prompt(
            tools,
            prefix=Agent_prefix,
            suffix=Agent_suffix,
            input_variables=["question"],
        )
        #7 agent_llm_chain 的创建
        agent_llm_chain = LLMChain(llm=self.task.llm, prompt=agnet_prompt)
        #8 创建agent代理
        agent = ZeroShotAgent(
            llm_chain=agent_llm_chain,
            tools=tools,
            verbose=False,
            stop=["\nObservation:"],   #设置停止方式
            )
        
        #9 创建agentchain代理
        agent_chain = AgentExecutor.from_agent_and_tools(
            agent=agent, 
            tools=tools, 
            verbose=True, 
            max_iterations=3,           # 最大轮数限制
            max_execution_time=2,       #最大时间限制 2s
            early_stopping_method="generate",#指定generate方法，然后对LLM进行一次最终通过以生成输出。
            handle_parsing_errors=True  # 处理解析错误并重试
        )
        
        return agent_chain
    
    
