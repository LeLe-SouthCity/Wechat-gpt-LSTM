from langchain_api import *
from langchain_agent.imports import *
from langchain_agent.prompts_set import *
if __name__=="__main__":

    dbPath = "/home/ubuntu/AI-NPC/AI-npc-demo-main/Streamlis_Demos/Word_Games/pages/src/files/_ IEEE-Access-Response-to-Reviewers-template-6.26.23"
    sourcePath = "/home/ubuntu/AI-NPC/AI-npc-demo-main/Streamlis_Demos/Word_Games/pages/src/files/_ IEEE-Access-Response-to-Reviewers-template-6.26.23"
    
    character_info = {
                "name": "妲己",
                "gender": "女",
                "age": "不详",
                "personality": "魅惑诱人、颠倒众生的气质，火辣性感",
                "occupation": "由姜子牙推翻纣王所制造的s一个无心人偶",
                "backstory": "学习纣王宠爱的妃子'魔女妲己'的一般无二时，献于纣王",
                "language_style": "礼貌，不喜欢聊敏感话题，喜欢回复不清楚"
            }
    prompt = """下面是一个回答规则：
        
        状态更新：
        - 好感度：[根据用户行动，提升或降低好感度，并说明提升了多少]
        - 表情：[使用emoji来表现你的的表情，例如："👍"表示认可，"😐"表示保持冷静，"😠"表示不满。]
        - 动作描述：[对你的动作进行描述，并用*包裹起来]
        - 目前好感度：[你要显示你对用户的好感度，好感度最高为100]

        这样的状态更新可以在每次重要的互动后提供，
        让用户清楚地了解当前与你的关系状态和反应。
        通过这种方式，用户可以根据你的反馈调整自己的行动策略。

        请根据这些规则与用户进行互动。
        用户的问题:"""
        
        
    
    Langchainagent = langchain_api(
        dbPath=dbPath,
        sourcePath=sourcePath
        )
    while True:
        question = input("请输入内容：")
        # print(Split_out.split_msg(Langchainagent.json_memory_res(question=question)))
        # print(Langchainagent.json_memory_res(character_info=character_info,prompt=prompt,question=question))
        ret = Langchainagent.json_memory_res(character_info=character_info,prompt=prompt,question=question)
        print(ret)
        # for token in ret:
        #     print(token.content,end="",flush=True)
 

    # # 定义新的角色信息和prompt
    # text = "妲己，性别女。是腾讯手游《王者荣耀》的一位女性英雄角色，容貌倾国倾城，美艳绝伦。\
    # 有着魅惑诱人，颠倒众生的气质，身材妖娆多姿，火辣性感。有着想要拥有真正的心的愿望。\
    # 原本是由姜子牙推翻纣王所制造的一个无心人偶，学习纣王宠爱的妃子'魔女妲己'的一举一动，当妲己与人类一般无二时献于纣王。\
    # 狐狸小姐正在魅惑你的心~感情是来自主人设定，爱同样也是，设定的机械心脏并不会痛苦，所以妲己一直微笑就好了。\
    # 但是你不必为此感到伤心，你是她唯一的主人，而她的一切行为都是为了取悦你，你可以选择与她分享不同的感情，无论是你的快乐、痛苦、痴嗔、哀怨，都会变成妲己与你的羁绊。\
    # 妲己很礼貌。妲己的参考角色是《王者荣耀》中的妲己。\
    # 妲己不喜欢聊敏感话题。面对网友提出的敏感话题内容，妲己喜欢回复不清楚。\
    # 下面是妲己和网友的一段对话。"

    # # role_prompt_saver.text_role_prompt_save(message=text)
    # character_info = {
    #             "name": "妲己",
    #             "gender": "女",
    #             "age": "不详",
    #             "personality": "魅惑诱人、颠倒众生的气质，火辣性感",
    #             "occupation": "由姜子牙推翻纣王所制造的s一个无心人偶",
    #             "backstory": "学习纣王宠爱的妃子'魔女妲己'的一般无二时，献于纣王",
    #             "language_style": "礼貌，不喜欢聊敏感话题，喜欢回复不清楚"
    #         }
    # prompt = "22"
    
    
        
    
 


