""""
Reflection agent范式
"""

from typing import Optional,Dict,Any,List

from ..core.config import Config

from ..core.agent import Agent

from ..core.llm import TAgentLLM

from ..core.message import Message

from ..tools.registry import ToolRegistry


DEFAULT_PROMPTS = {
    "initial": """
请根据以下要求完成任务:

任务: {task}

请提供一个完整、准确的回答。
""",
    "reflect": """
请仔细审查以下回答，并找出可能的问题或改进空间:

# 原始任务:
{task}

# 当前回答:
{content}

请分析这个回答的质量，指出不足之处，并提出具体的改进建议。
如果回答已经很好，请回答"无需改进"。
""",
    "refine": """
请根据反馈意见改进你的回答:

# 原始任务:
{task}

# 上一轮回答:
{last_attempt}

# 反馈意见:
{feedback}

请提供一个改进后的回答。
"""
}


class ReflectAgent(Agent):
    def __init__(
            self,
            name:str,
            llm:TAgentLLM,
            tool_registry:ToolRegistry,
            system_prompt:Optional[str]=None,
            config:Optional[Config]=None,
            max_steps:int=5,
            custom_prompt:Optional[str]=None):
            """
            Args:
                name (str): Agent名称
                llm (TAgentLLM): 语言模型实例
                tool_registry (ToolRegistry): 工具注册表
                system_prompt (Optional[str], optional): 系统提示语. Defaults to None.
                config (Optional[Config], optional): 配置对象. Defaults to None.
                max_steps (int, optional): 最大推理步骤数. Defaults to 5.
                custom_prompt (Optional[str], optional): 自定义提示语模板. Defaults to None.
            """
            super().__init__(name, llm, system_prompt, config)
            self.tool_registry = tool_registry
            self.max_steps = max_steps
            self.current_history: List[str] = []

            self.prompt_template = custom_prompt or DEFAULT_PROMPTS

    def run(self, input_text:str,**kwargs):

        prompt = ""
        response_text = ""
        last_resoponse_text = ""
        feedback_text = ""

        for i in range(self.max_steps):
            
            if i == 0:
                prompt = self.prompt_template["initial"].format(task = input_text)
            else:
                prompt = self.prompt_template["refine"].format(
                    task = input_text,
                    last_attempt = response_text,
                    feedback = feedback_text)
            last_resoponse_text = response_text    
            response_text = self.llm.answer([{"content":prompt,"role":"user"}])

            if response_text == "无需改进":
                return  last_resoponse_text
            
            reflect_prompt = self.prompt_template["reflect"].format(
                task = input_text,
                content = response_text)
            
            feedback_text = self.llm.answer([{"content":reflect_prompt,"role":"assistant"}])

        return None

            
