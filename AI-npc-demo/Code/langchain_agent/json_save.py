from langchain_agent.imports import *

    
class JsonRolePromptSave:
    """
    专门创建的角色数据库
    """
    def __init__(
        self,
        file_path="characters.json"
        ):
        """
        这会在目录下创建一个角色的json数据库
        """
        self.file_path = Path(file_path)
        # 确保文件存在，如果不存在则创建一个空的角色列表
        if not self.file_path.is_file():
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump({"characters": []}, f, indent=4, ensure_ascii=False)
        
        # 读取现有数据
        with open(self.file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            #self保存现有数据
            self.data = data
            
    def dict_character_and_prompt_as_json(
        self,
        character_info:dict,
        prompt:str
        ):
        """
        保存字典类型的数据数据
        prompt(str):角色的prompt设定
        """
        # 读取现有数据
        with open(self.file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        #self保存现有数据
        self.data = data
        #self保存该角色
        self.character_info = character_info
        # 检查角色是否已存在
        if any(char["character_info"] == character_info for char in data["characters"]):
            print("Character already exists. Skipping...")
            return
        
        # 添加新角色信息和prompt
        data["characters"].append({
            "character_info": character_info,
            "prompt": prompt,
            "history":["user: 你好"]
        })
        
        
        
        # 保存更新后的数据
        with open(self.file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        print("Character info saved.")
    
    def str_role_prompt_save(
            self, 
            message: str,
            prompt:str
        ):
        """
        针对str的一段话内容进行优化成字典类型，再保存
        message(str): 角色内容的输入
        """
        character_info = self.str_role_history_Optimization(message=message)
        print("character_info",character_info)
        self.dict_character_and_prompt_as_json(character_info=character_info,prompt=prompt)
    
    def str_role_history_Optimization(
            self, 
            message: str, 
            max_tokens: int = 4000
        ):
        """
        将text保存重要的内容，并转换成需要得格式
        message(str): 历史记录的输入
        max_tokens (int) : 最大token限制
        """
        # Calculate the total number of tokens in the message
        token_count = self.num_tokens_from_messages(messages=message)
        print("str Token count:", token_count)
        
        # If the number of tokens is within the limit, return the original message
        if token_count <= max_tokens:
            llmprompt = self.get_role_message_llm_prompt(prompt=message)
            role_message = OpenAI(temperature=1.0)(llmprompt)
            role_message = self.str_to_dict(character_str=role_message)
            print(type(role_message))
            return role_message

        # Split the history into chunks based on token count
        optimized_chunks = []
        start_index = 0
        while start_index < len(message):
            # Try to get a chunk with the maximum number of tokens
            end_index = start_index + max_tokens
            chunk = message[start_index:end_index]

            # Calculate the token count for the chunk
            chunk_token_count = self.num_tokens_from_messages(messages=chunk)

            # If the chunk's token count exceeds the limit, shorten the chunk
            while chunk_token_count > max_tokens and end_index > start_index:
                end_index -= 1
                chunk = message[start_index:end_index]
                chunk_token_count = self.num_tokens_from_messages(messages=chunk)
                llmprompt = self.LLM_token_OP_prompt(message=chunk, max_tokens=max_tokens)
            # Optimize the chunk using the language model
            optimized_chunk = OpenAI(temperature=1.0)(llmprompt)
            print("Optimized chunk:", optimized_chunk)
            optimized_chunks.append(optimized_chunk)

            # Update the start index to process the next chunk
            start_index = end_index

        # Combine the optimized chunks
        optimized_history = ''.join(optimized_chunks)
        chunk_token_count = self.num_tokens_from_messages(messages=optimized_history)
        
        llmprompt = self.get_role_message_llm_prompt(message=chunk)
        role_message = OpenAI(temperature=1.0)(llmprompt)
        print("optimized_history:", optimized_history)
        role_message = self.str_to_dict(character_str=role_message)
        # Return the optimized history
        return role_message
      
    def LLM_token_OP_prompt(
        self,
        message:str,
        max_tokens:int
        ):
        """
        优化角色信息以适应token的限制
        message(str): 角色信息
        max_tokens (int) : 最大token限制
        """
        LLM_task_prompt=f"""
            我有一个任务给你。 我需要您帮助我优化这段对话内容以适应 {max_tokens} 个令牌的限制。 \
            谈话很长，我想确保我们尽可能的留关键的信息。\
            以下是对话的内容：
            {message}
            """  
        return LLM_task_prompt
    
    def get_role_message_llm_prompt(
        self,
        prompt:str
        ):
        """
        保留重要的历史记录设置的prompt
        prompt(str): 历史记录
        """
        task_prompt=f"""
            我有一个任务给你。 我需要将这个一段包含用户信息的文本"{prompt}"归纳成以下格式
            请记住一定要按照以下格式
            格式：
            name: 张三3
            gender: 男
            age: 35
            personality: 冷静而严谨
            occupation: 科学家
            backstory: 一位致力于研究未知领域的科学家。
            language_style: 语言精确，喜欢用科学术语。
            """  
        return task_prompt
     
    def num_tokens_from_messages(self, messages, model="gpt-3.5-turbo-0613"):
        """Return the number of tokens used by a list of messages where each message is a string.
            总之就是token的计算
        """
        try:
            encoding = tiktoken.encoding_for_model(model)
        except KeyError:
            print("Warning: model not found. Using cl100k_base encoding.")
            encoding = tiktoken.get_encoding("cl100k_base")
        if model in {
            "gpt-3.5-turbo-0613",
            "gpt-3.5-turbo-16k-0613",
            "gpt-4-0314",
            "gpt-4-32k-0314",
            "gpt-4-0613",
            "gpt-4-32k-0613",
            }:
            tokens_per_message = 3
        elif model == "gpt-3.5-turbo-0301":
            tokens_per_message = 4
        elif "gpt-3.5-turbo" in model:
            print("Warning: gpt-3.5-turbo may update over time. Returning num tokens assuming gpt-3.5-turbo-0613.")
            return self.num_tokens_from_messages(messages, model="gpt-3.5-turbo-0613")
        elif "gpt-4" in model:
            print("Warning: gpt-4 may update over time. Returning num tokens assuming gpt-4-0613.")
            return self.num_tokens_from_messages(messages, model="gpt-4-0613")
        else:
            raise NotImplementedError(
                f"""num_tokens_from_messages() is not implemented for model {model}. See https://github.com/openai/openai-python/blob/main/chatml.md for information on how messages are converted to tokens."""
            )
        num_tokens = 0
        for message in messages:
            num_tokens += tokens_per_message
            num_tokens += len(encoding.encode(message))
        num_tokens += 3  # every reply is primed with <|im_start|>assistant<|im_sep|>
        return num_tokens
    
    def dialog_save(self, characterName: str, message: str):
        # 检查角色是否已存在
        for character in self.data["characters"]:
            # 比较 character_info 字典是否与 self.character_info 完全匹配
            if character["character_info"] == self.character_info:
                print("角色存在")
                # 创建一个新的历史记录条目
                new_entry = f"""{characterName}: {message}"""
                # 添加到历史记录列表中
                character["history"].append(new_entry)
                # 保存更新后的数据
                with open(self.file_path, 'w', encoding='utf-8') as f:
                    json.dump(self.data, f, indent=4, ensure_ascii=False)
                break
        else: 
            print("角色不存在")

    def get_dialog(self):
        for character in self.data["characters"]:
            # 比较 character_info 字典是否与 self.character_info 完全匹配
            if character["character_info"] == self.character_info:
                print("该角色的对话记录存在")
                return character["history"]
            else:
                # 如果角色不存在，则返回一个空列表或者None
                print(f"角色不存在。")
                return None
    
    def rewrite_character_history(
        self, 
        # character_info: dict, 
        new_history: list):
        """
        重写该角色的历史记录
        """
        # 检查角色是否已存在
        for character in self.data["characters"]:
            # 比较 character_info 字典是否与传入的 character_info 完全匹配
            if character["character_info"] == self.character_info:
                print("找到匹配的角色，正在重写历史记录。")
                # 重写历史记录
                character["history"] = new_history
                # 保存更新后的数据
                with open(self.file_path, 'w', encoding='utf-8') as f:
                    json.dump(self.data, f, indent=4, ensure_ascii=False)
                break
        else:
            print("没有找到匹配的角色。")

    def str_to_dict(
        self,
        character_str:str
        ):
        """
        字符串->字典
        """
        print("using str_to_dict---")
        # 将字符串按行分割
        character_info_lines = character_str.strip().split('\n')

        # 创建一个空字典来存储新的角色信息
        character_info_dict = {}

        # 遍历每一行
        for line in character_info_lines:
            # 将每一行按冒号分割为键和值
            key, value = line.split(':', 1)
            character_info_dict[key.strip()] = value.strip()
        return character_info_dict
    
    def dict_to_str(
        self,
        character_info:dict,
        ):
        """字典-》str"""
        # 转换字典为JSON字符串
        character_info_str = json.dumps(character_info, ensure_ascii=False, indent=4)
        # 移除字符串中的大括号
        character_info_str = character_info_str.replace("{", "").replace("}", "")
        
        return character_info_str
    
    def convert_to_list(
        self,
        input_data
        ):
        if isinstance(input_data, str):
            try:
                return ast.literal_eval(input_data)
            except SyntaxError:
                # 如果发生语法错误，打印错误信息并返回一个空列表或其他默认值
                print("convert_to_list encountered a SyntaxError")
                return []
        else:
            # 如果 input_data 已经是列表，则直接返回它
            return input_data
        # try:
        #     return ast.literal_eval(input_data)
        # except SyntaxError:
        #     # 如果发生语法错误，打印错误信息并返回一个空列表或其他默认值
        #     print("convert_to_list encountered a SyntaxError")
        #     return []
     
    # def read_json_memory(
    #     self,
        
    # ):
        
        
          