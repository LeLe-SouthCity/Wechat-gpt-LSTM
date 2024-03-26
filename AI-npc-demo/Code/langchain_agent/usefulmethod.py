from langchain_agent.imports import *

from langchain.schema.messages import BaseMessage, _message_to_dict, messages_from_dict
#Get LLM model 
class LLM_Model():
    """
    提供多个Model模型 名称以及选择
    1、Openai 
       model : 
            model name          token
            "gpt-3.5-turbo" —— 4097 
            "gpt-4"         ——  8192
            "gpt-3.5-turbo-instruct" —— 4097

    2、ChatGLM 
    endpoint_url = "http://10.18.0.136:8000"        
            
    3、Minimax 
       model : 
            model name          token
            "abab5-chat"        6144
            "abab5.5-chat"      16384
            "embo-01"           Embedding(向量化)
            "speech-01"         vedio(语音生成/长文本语音)
    """
    def __init__(
            self,
            llm_model_type :int = 1,
            temperature : float = 0.7
        ):
        """
        llm_model_type (int) : openai=1 Get_ChatGLM=2 minimax=3
        temperature (float): 样本值 值越大越随机
        """
        os.environ["OPENAI_API_KEY"] =os.getenv('OPENAI_API_KEY')
        self.llm_model_type = llm_model_type
        self.temperature = temperature

    def Get_openaiLLM(
                self,
                modelname: str = "gpt-3.5-turbo"
            ):
        """
        args:
        获取 Openai 语言模型
        modelname (str): model选择的名称
            "gpt-3.5-turbo" —— 4097 
            "gpt-4"  ——  8192
            "gpt-3.5-turbo-instruct" —— 4097
        """
        
        
        # 创建大语言模型对象
        llm_openai = ChatOpenAI(model=modelname,temperature=self.temperature)

        return llm_openai
    
    def Get_ChatGLM(
                self
            ):
        """
        args:
        获取ChatGLM语言模型
        """
        # http://14.136.93.113:8000/v1/chat/completions 
        endpoint_url = "http://14.136.93.113:8000/v1/chat/completions"
        llm = ChatGLM(
            endpoint_url=endpoint_url,
            max_token=80000,
            top_p=self.temperature,
        )

        return llm
    
    def Get_minimaxLLM(
                self,
                modelname: str = "abab5-chat"
            ):
        """
        args:
        获取 Minimax的语言模型

        temperature (float): 样本值 0-1 值越高越随机
        modelname (str): model选择的名称,\
        "abab5-chat" —— \
        "abab5.5-chat" —— \
        "embo-01" —— \
        "speech-01"  """

        os.environ["MINIMAX_GROUP_ID"] = "1697689414438479"
        os.environ["MINIMAX_API_KEY"] = os.getenv('MINIMAX_API_KEY')

        # 创建minimax大语言模型对象
        
        
        llm_minimax = Minimax(
                                model=modelname, 
                                minimax_api_key=
                                    os.getenv('MINIMAX_API_KEY'),
                                minimax_group_id="1697689414438479",
                                temperature = self.temperature
                            )
        return llm_minimax
    
    def get_model(
                self,
                modelname
            ):
        """
        args:
        获取 Openai 语言模型
        modelname (str): openai="gpt-3.5-turbo"  minimax="abab5.5-chat"
        """
        if self.llm_model_type==1:
            return self.Get_openaiLLM(modelname)
        elif self.llm_model_type==2:
            return self.Get_ChatGLM()
        elif self.llm_model_type==3:
            return self.Get_minimaxLLM(modelname)
        else :
            raise ValueError("输入的值错误，无法返回模型,llm_model_type的值应在1-3中选择")


# Set up a prompt template
class CustomPromptTemplate(BaseChatPromptTemplate):
    # The template to use
    template: str
    # The list of tools available
    tools: List[Tool]

    def format_messages(self, **kwargs) -> str:
        # Get the intermediate steps (AgentAction, Observation tuples)
        # Format them in a particular way
        intermediate_steps = kwargs.pop("intermediate_steps")
        thoughts = ""
        for action, observation in intermediate_steps:
            thoughts += action.log
            thoughts += f"\nObservation: {observation}\nThought: "
        # Set the agent_scratchpad variable to that value
        kwargs["agent_scratchpad"] = thoughts
        # Create a tools variable from the list of tools provided
        kwargs["tools"] = "\n".join([f"{tool.name}: {tool.description}" for tool in self.tools])
        # Create a list of tool names for the tools provided
        kwargs["tool_names"] = ", ".join([tool.name for tool in self.tools])
        formatted = self.template.format(**kwargs)
        return [HumanMessage(content=formatted)]
    
# setting CustomutputParser 
class CustomOutputParser(AgentOutputParser):

    def parse(self, llm_output: str) -> Union[AgentAction, AgentFinish]:
        # Check if agent should finish
        if "Final Answer:" in llm_output:
            return AgentFinish(
                # Return values is generally always a dictionary with a single `output` key
                # It is not recommended to try anything else at the moment :)
                return_values={"output": llm_output.split("Final Answer:")[-1].strip()},
                log=llm_output,
            )
        # Parse out the action and action input
        regex = r"Action\s*\d*\s*:(.*?)\nAction\s*\d*\s*Input\s*\d*\s*:[\s]*(.*)"
        match = re.search(regex, llm_output, re.DOTALL)
        if not match:
            raise ValueError(f"Could not parse LLM output: `{llm_output}`")
        action = match.group(1).strip()
        action_input = match.group(2)
        # Return the action and action input
        return AgentAction(tool=action, tool_input=action_input.strip(" ").strip('"'), log=llm_output)


