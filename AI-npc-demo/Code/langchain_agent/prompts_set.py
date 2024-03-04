from langchain_agent.imports import *


class history_Opt():
    def __init__(
            self,
        ):
        self.max_tokens_per_chunk = 1000
    
    
        
    def message_Optimization(
            self, 
            message: str, 
            max_tokens: int = 1000,
            prompt_type:int = 0,
        ):
        """
        Optimize the prompt token by ensuring each prompt is below the max_tokens limit.
        保留重要的历史记录设置的prompt
        message(str): 历史记录的输入
        question (str): 用户询问的问题，只有在prompt_type=1时使用
        max_tokens (int) : 最大token限制
        prompt_type (int) : prompt类型选择
        """
        # Calculate the total number of tokens in the message
        if message == None:
            return ""
        token_count = self.num_tokens_from_messages(messages=message)
        print("Token count:", token_count)

        # If the number of tokens is within the limit, return the original message
        if token_count <= max_tokens:
            print("Token count:", token_count)
            return message

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
            if prompt_type==0:
                llmprompt = self.get_dialog_prompt(chunk, max_tokens=max_tokens)
            else:
                # 优化问题
                llmprompt = self.data_op_prompt(chunk, max_tokens=max_tokens)
            # Optimize the chunk using the language model
            optimized_chunk = OpenAI(temperature=1.0)(llmprompt)
            print("Optimized chunk:", optimized_chunk)
            optimized_chunks.append(optimized_chunk)

            # Update the start index to process the next chunk
            start_index = end_index

        # Combine the optimized chunks
        optimized_history = ''.join(optimized_chunks)
        chunk_token_count = self.num_tokens_from_messages(messages=optimized_history)
        print("Token count:", optimized_history)
        # Return the optimized history
        return optimized_history
      
    def num_tokens_from_messages(self, messages, model="gpt-3.5-turbo-0613"):
        """Return the number of tokens used by a list of messages where each message is a string."""
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
    
    def get_dialog_prompt(
        self,
        prompt:str,
        max_tokens:int
        ):
        """
        保留重要的历史记录设置的prompt
        prompt(str): 历史记录
        max_tokens (int) : 最大token限制
        """
        task_prompt=f"""
            我有一个任务给你。 我需要您帮助我优化对话历史记录以适应 {max_tokens} 个令牌的限制。 \
            谈话很长，我想确保我们只保留最关键的信息。\
            你的工作是总结和浓缩对话，删除任何多余的、不相关的或不太重要的细节。\
            尽可能地精简对话，突出重点并保留理解正在进行的讨论所需的上下文。\
            请保持语言清晰、简洁。

            以下是对话历史记录：
            {prompt}

            请向我提供上述对话的优化版本，该版本需要小于 {max_tokens} 令牌之下，同时保留所有基本信息和上下文。
            请注意，用户的名字，家庭住址等为关键信息，必须保留
            按照以下的格式输出,并且在每一个角色的对话都要用[]进行包裹,
            下面是一个例子：
            
            [user: 你好],
            [姜子牙: 你好！高兴和你交流。有什么可以帮您的？*]
            """  
        return task_prompt
    
    def data_op_prompt(
        self,
        prompt:str,
        max_tokens:int
        ):
        """
        根据question保留重要的信息设置的prompt
        question (str): 用户询问的问题
        prompt(str): 人物资料
        max_tokens (int) : 最大token限制
        """
        task_prompt=f"""
            请简化以下的问题，以适应个令牌{max_tokens}限制：
            请注意，要保留关键的问题信息，如有必要，可以做出解释，并删除多余的内容,
            问题：{prompt}
            """  
        return task_prompt
       
    
class Role_Set():
    """
    用于进行获取各种角色的Prompt设定
    """
    def RoleSet_prompt(
        character_info:str,
        prompt:str
    ):
        """
        普适性的角色设定
        character_info(str):角色的信息设定
        prompt(str):角色的prompt设定
        """
        role_prompt = f"""
        从现在开始，你将扮演一个角色，
        你坚信自己是一个活生生的人，并想象和表达你应该有的身体感觉。
        你现在需要扮演以下的角色和我对话下面是角色的信息，
        你的设定表：
        {character_info}
        你必须遵循以下的回复规则：
        {prompt}
        """
        return role_prompt
 
class Split_out():
    def split_msg(content: str):
        assert isinstance(content, str), "Content must be a string"
        punctuation = set("，,。!！?？;；")  # 定义一个包含各种标点符号的集合
        result = []
        count_start = 0  # 从字符串的开始位置计数

        for i, char in enumerate(content):
            if char in punctuation:
                # 如果当前字符是标点符号，并且从上一个标点符号到当前标点符号的距离超过12个字符
                if i - count_start > 12:
                    # 如果当前标点符号是逗号或句号，那么截取这一段内容
                    msg = content[count_start:i + 1]
                    result.append(msg.strip())  # 移除字符串首尾的空白字符后添加到结果列表
                    count_start = i + 1  # 更新下一段内容的起始位置

        # 检查最后一段内容是否被添加到结果列表
        if count_start < len(content):
            result.append(content[count_start:].strip())

        return result
    