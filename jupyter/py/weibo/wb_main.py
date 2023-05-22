import os
import re
import copy
import torch
import platform
from langchain.prompts import PromptTemplate
from langchain.llms import OpenAI
from langchain.chains import LLMChain
import os
os.environ["OPENAI_API_KEY"] = "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"
from weibo import WeiboApi


def main():
    template = """
{content}, This is a message posted by a blogger on Weibo. Please reply to the message in the tone of a user. 
The style is required to be humorous and interesting. You can write it based on the following examples. 
Example 1:{example1},Example 2:{example2},Example 3:{example3}. And answer in Chinese.
"""

    llm = OpenAI(temperature=0.9)
    prompt = PromptTemplate(
    input_variables=["content", "example1","example2","example3"],
    template=template,
    )
    
    chain = LLMChain(llm=llm, prompt=prompt)
    print("欢迎使用微博评论自动回复，输入微博用户账户即可进行对用户最近的10条微博进行回复，clear 清空对话历史，stop 终止程序")
    while True:
        query = input("\n🧑请输入微博用户ID或昵称：")
        if query == "stop":
            break
        if query == "clear":
            history = []
            command = 'cls' if os_name == 'Windows' else 'clear'
            os.system(command)
            print("欢迎使用微博评论自动回复，输入微博用户账户即可进行对用户最近的3条微博进行回复，clear 清空对话历史，stop 终止程序")
            continue
        input_list = getWeiboInputList(query=query)
        j=1
        for input_var in input_list:
            print(query,'的第',str(j),'条微博 ',input_var['created_at'],' 点赞数:',input_var['attitudes_count'],' :',input_var['content'])
            resp = chain.run(input_var)
            if "很抱歉" in resp:
                continue
            print('>>>AI自动回复:',resp.strip())
            print('===================================')
            j=j+1

def getWeiboInputList(query):
    input_list = []
    uid =None
    name=None
    if isinstance(query, int) or isinstance(query, float):
        uid=query
    else:
        name = query 
    weiboApi = WeiboApi() 
    resp = weiboApi.get_user_weibo_info(uid=uid,screen_name=name)
    weiboList = resp['weibolist']
    user = resp['user']
    
    for weiboInfo in weiboList:
        input_variables = dict()
        input_variables['content'] = weiboInfo['content']
        input_variables['created_at'] = weiboInfo['created_at']
        input_variables['attitudes_count'] = weiboInfo['attitudes_count']
        i=1
        comments = weiboInfo['comments']
        for comment in comments:
            input_variables['example'+str(i)] = comment['content']
            i=i+1
            if i>3:
                break
        input_list.append(input_variables)
    return input_list 
   
    
if __name__ == "__main__":
    main()
