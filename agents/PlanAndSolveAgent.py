""""
Plan-and-Solve agent范式
"""
import ast

from typing import Optional,Dict,Any,List

from ..core.config import Config

from ..core.agent import Agent

from ..core.llm import TAgentLLM

from ..core.message import Message

from ..tools.registry import ToolRegistry

# 默认规划器提示词模板
DEFAULT_PLANNER_PROMPT = """
你是一个顶级的AI规划专家。你的任务是将用户提出的复杂问题分解成一个由多个简单步骤组成的行动计划。
请确保计划中的每个步骤都是一个独立的、可执行的子任务，并且严格按照逻辑顺序排列。
你的输出必须是一个Python列表，其中每个元素都是一个描述子任务的字符串。

问题: {question}

请严格按照以下格式输出你的计划:
```python
["步骤1", "步骤2", "步骤3", ...]
```
"""

# 默认执行器提示词模板
DEFAULT_EXECUTOR_PROMPT = """
你是一位顶级的AI执行专家。你的任务是严格按照给定的计划，一步步地解决问题。
你将收到原始问题、完整的计划、以及到目前为止已经完成的步骤和结果。
请你专注于解决"当前步骤"，并仅输出该步骤的最终答案，不要输出任何额外的解释或对话。

# 原始问题:
{question}

# 完整计划:
{plan}

# 历史步骤与结果:
{history}

# 当前步骤:
{current_step}

请仅输出针对"当前步骤"的回答:
"""


class PlanAndSolveAgent(Agent):
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

            self.prompt_planner_template = custom_prompt or DEFAULT_PLANNER_PROMPT
            self.prompt_executor_template = DEFAULT_EXECUTOR_PROMPT


    def _parse_plan_steps(input_text:str) -> List[str]:
        steps = ast.literal_eval(input_text)
        return steps

    def run(self, input_text, **kwargs):
        plan_prompt = self.prompt_planner_template.format(
             question = input_text
        )

        response_text = self.llm.answer(messages=[{"content":plan_prompt,"role":"user"}])

        plan_steps = self._parse_plan_steps(response_text)

        steps = len(plan_steps)

        for step_count in range(steps):
            history_str = "\n".join(self.current_history)
            executor_prompt = self.prompt_executor_template.format(
                question = input_text,
                plan = response_text,
                history = history_str,
                current_step = plan_steps[step_count]
            )

            response_text = self.llm.answer([{"content":executor_prompt,"role":"user"}])
            
            self.current_history.append(executor_prompt+response_text)

            if step_count == steps -1:
                self.add_message_to_history(message=Message(content=input_text,role="user"))
                self.add_message_to_history(message=Message(content=response_text,role="assistant")) 

                return response_text
        return None




