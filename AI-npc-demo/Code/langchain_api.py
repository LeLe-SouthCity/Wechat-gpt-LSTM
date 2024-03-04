from langchain_agent.function import *
from langchain_agent.usefulmethod import *
from langchain_agent.json_save import *

class langchain_api():
    def __init__(
            self,
            temperature:float=0.7,
            dbPath:str =  "AI-npc-demo-main/Source/npc_database/DB-Levi Ackerman",
            sourcePath:str = "AI-npc-demo-main/Source/npcs/Levi_Ackerman",
        ):
        """
        专门用于提供langchain接口的代码
        """
        # 谷歌搜索的Key
        self.temperature = temperature
        self.llm = LLM_Model(llm_model_type=1,temperature = temperature).get_model(modelname="gpt-3.5-turbo")
        self.dbPath = dbPath
        self.sourcePath = sourcePath
        
     
    def Json_memory_Save(
        self,
        character_info,
        prompt,
    )->JsonRolePromptSave:
        """
        主要用户获取一个有实体的JsonRolePromptSave类
        这个类已经包含了角色的信息和prompt
        """
        json_memory = JsonRolePromptSave()
        # 检查 character_info 是否是字符串类型
        if isinstance(character_info, str):
            print("character_info 是字符串类型")
            json_memory.str_role_prompt_save(
                character_info=character_info,
                prompt=prompt
            )
        # 检查 character_info 是否是字典类型
        elif isinstance(character_info, dict):
            print("character_info 是字典类型")
            json_memory.dict_character_and_prompt_as_json(
                character_info=character_info,
                prompt=prompt
            )
        else:
            print("目前仅支持str与dict格式")
        
        return json_memory
    
    def json_memory_res(
        self,
        character_info,
        prompt:str,
        question:str,
        ):
        MAX_SUM_TOKEN=4097        
        # 获取数据库类
        Json_memory = self.Json_memory_Save(
                character_info=character_info,
                prompt=prompt
        )
        # 判断question是否过大，过大则优化
        if history_Opt().num_tokens_from_messages(question)>1000:
            question = history_Opt().message_Optimization(message=question,prompt_type=1)
            
        print("初始对话",Json_memory.get_dialog())
        history = history_Opt().message_Optimization(message = Json_memory.get_dialog())
        # 获取角色的prompt（这个是总prompt）
        prefix = Role_Set.RoleSet_prompt(
            character_info=Json_memory.dict_to_str(character_info),
            prompt = prompt
        )
        prefix1 = f"""{prefix}
        下面是我与你对话的历史记录。\
        {history}
        """
        print("prefix1是：",prefix1)
        print("优化后的历史记录",history)
        
        Json_memory.rewrite_character_history(new_history=Json_memory.convert_to_list(input_data=history))
        
        # 数据库向量化
        vector_store = KnownLedge2Vector(
                            dbpath=self.dbPath,
                            datasetdir=self.sourcePath,
                            model_name=1
                        ).init_vector_store()
        
        # 任务类
        task = MyTask(
            llm=self.llm,
            retriever=vector_store.as_retriever(
                search_type="mmr",
                search_kwargs={'k': 3, 'fetch_k': 50, 'lambda_mult': 0.25}
            )
        )
        # 创建代理类
        vecagent = Vect_Agent(vector_store=vector_store,task=task)
        max_retries = 3  # 设置最大重试次数
        attempts = 0     # 初始化尝试次数
        Json_memory.dialog_save(characterName="user",message=question)
        print("类型",type(question))
        # 报错再试
        while attempts < max_retries:
            try:
                # 尝试执行可能会引发异常的代码
                res = vecagent.agentchain_memory_json_latest(prefix=prefix1).run(question)
                # res = vecagent.agentchain_memory_json_latest(prefix=prefix1).stream({"query": question})
                #保存用户提出的问题和回答
                
                Json_memory.dialog_save(characterName=character_info['name'],message=res)
                return res
            except Exception as e:
                # 如果发生异常，打印错误消息并重试
                print(f"An error occurred: {e}")
                attempts += 1  # 增加尝试次数

                if attempts == max_retries:
                    print("Max retries reached. Unable to complete the operation.")
                    # 在这里可能需要执行一些清理工作或者抛出异常
                    # raise e  # 可以选择重新抛出异常或者终止程序
        
        return f"Error"
        
       




