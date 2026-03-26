""""
ReAct agent范式
"""
import re
from typing import Optional, Dict, Any, List, Tuple

from ..core.config import Config

from ..core.agent import Agent

from ..core.llm import TAgentLLM

from ..tools.registry import ToolRegistry

from ..core.message import Message


DEFAULT_REACT_PROMPT = """你是一个具备推理和行动能力的AI助手。你可以通过思考分析问题，然后调用合适的工具来获取信息，最终给出准确的答案。

## 可用工具
{tools}

## 工作流程
请严格按照以下格式进行回应，每次只能执行一个步骤：

**Thought:** 分析当前问题，思考需要什么信息或采取什么行动。
**Action:** 选择一个行动，格式必须是以下之一：
- `{{tool_name}}[{{tool_input}}]` - 调用指定工具
- `Finish[最终答案]` - 当你有足够信息给出最终答案时

## 重要提醒
1. 每次回应必须包含Thought和Action两部分
2. 工具调用的格式必须严格遵循：工具名[参数]
3. 只有当你确信有足够信息回答问题时，才使用Finish
4. 如果工具返回的信息不够，继续使用其他工具或相同工具的不同参数

## 当前任务
**Question:** {question}

## 执行历史
{history}

现在开始你的推理和行动："""



class ReActAgent(Agent):
    
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

            self.prompt_template = custom_prompt or DEFAULT_REACT_PROMPT

    @staticmethod
    def _parse_llm_result(text: str) -> Tuple[str, str]:
          """
          从LLM响应中提取 Thought 和 Action。
          支持如下形式：
          Thought: ...\nAction: ...
          **Thought:** ...\n**Action:** ...
          """
          thought_match = re.search(
                r"(?:\*\*)?Thought(?:\*\*)?\s*[:：]\s*(.*?)(?=\n\s*(?:\*\*)?Action(?:\*\*)?\s*[:：])",
                text,
                flags=re.IGNORECASE | re.DOTALL,
          )
          action_match = re.search(
                r"(?:\*\*)?Action(?:\*\*)?\s*[:：]\s*(.+)",
                text,
                flags=re.IGNORECASE | re.DOTALL,
          )

          thought = thought_match.group(1).strip() if thought_match else ""
          action_block = action_match.group(1).strip() if action_match else ""
          action = action_block.splitlines()[0].strip() if action_block else ""

          if not thought or not action:
                raise ValueError(f"LLM输出格式错误，无法解析Thought/Action: {text}")

          return thought, action
    
    def run(self, input_text:str,**kwargs) -> str:
            self.current_history = []
            current_step = 0

            print(f"🤖 {self.name} 开始处理问题: {input_text}")


            while current_step < self.max_steps:
                    current_step += 1

                    print(f"\n--- 步骤 {current_step} ---")

                    ### 构建提示语
                    tools_desc = self.tool_registry.get_tool_description()

                    history_str = "\n".join(self.current_history)

                    prompt = self.prompt_template.format(
                        tools=tools_desc,
                        question=input_text,
                        history = history_str)
                    
                    # 调用 llm
                    messages = [{"role":"user","content":prompt}]

                    response_text = self.llm.answer(messages=messages,
                                                    stream=True)

                    thought, action = self._parse_llm_result(response_text)
                    print(f"Thought: {thought}")
                    print(f"Action: {action}")


                    match = re.match(r"(.*?)\[(.*)\]", action)
                    if match:
                        tool_name = match.group(1)
                        tool_input = match.group(2)

                        tool_result = self.tool_registry.excute_tool(name=tool_name,input_text=tool_input)

                        self.current_history.append(f"Action: {action}")
                        self.current_history.append(f"Observation: {tool_result}")
                    else:
                        self.add_message_to_history(Message(content=input_text,role="user"))
                        result = re.search(r"Finish\[(.*?)\]", action)
                        self.add_message_to_history(Message(content=result,role="assistant"))
                        return result
            
            final_result = "抱歉，我未能在规定步数之内完成任务"
            self.add_message_to_history(Message(content=input_text,role="user"))
            self.add_message_to_history(Message(content=final_result,role="assistant"))
            return final_result
                

                

                
                      