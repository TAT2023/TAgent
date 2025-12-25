
import os

from openai import OpenAI

from dotenv import load_dotenv

from typing import List,Dict


load_dotenv()



class TAgentLLM:
    '''
    llm的调用服务类，可以调用任何兼容OpenAI接口的服务，并默认使用流式响应
    '''
    def __init__(self,model_name:str=None,api_key:str=None,base_url:str=None,timeout:int=None):
        self.model_name=model_name or os.getenv("LLM_MODEL_ID")
        self.api_key=api_key or os.getenv("LLM_API_KEY")
        self.base_url=base_url or os.getenv("LLM_BASE_URL")
        self.timeout=timeout or int(os.getenv("LLM_TIMEOUT",60))

        if not all ([self.model_name,self.api_key,self.base_url]):
            raise ValueError("LLM model_name, api_key, base_url must be provided either as arguments or environment variables.")
        
        self.llm_client = OpenAI(api_key=self.api_key, api_base=self.base_url, timeout=self.timeout)
    
    def answer(self,messages:List[Dict[str,str]],temprerature:float=0.0,stream:bool=True)->str:
        '''
        调用llm接口获取回答
        messages: List[Dict[str,str]] 消息列表，格式参考OpenAI的chat.completions接口
        stream: bool 是否使用流式响应，默认True
        '''
        print(f"🧠 正在调用 {self.model_name} 模型...")

        try:
            response = self.llm_client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=temprerature,
                stream=stream
            )
            if stream:
                answer_chunks = []
                for chunk in response:
                    delta = chunk.choices[0].delta
                    if 'content' in delta:
                        content = delta['content']
                        answer_chunks.append(content)
                        print(content, end='', flush=True)
                print()  # Print a newline after the streaming is done
                return ''.join(answer_chunks)
            else:
                answer = response.choices[0].message['content']
                print(answer)
                return answer
        except Exception as e:
            print(f"❌ 调用LLM接口出错: {e}")
            return ""