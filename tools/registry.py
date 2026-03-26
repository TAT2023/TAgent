
"""工具注册类"""

from typing import Optional,Dict,Type,Callable,List

from tool import Tool


class ToolRegistry:

    """
    支持两种工具注册方式：
    1.Tool对象注册
    2.函数注册
    """

    def __init__(self):
        self._tools:Dict[str,Tool]={}

        self._functions:Dict[str,dict[str,any]] = {}


    def register_rool(self,tool:Tool):
        """
        注册Tool对象
        """

        if tool.name in self._tools:
            print(f"⚠️ 工具 {tool.name} 已存在,已有工具将被覆盖。")
        
        self._tools[tool.name]=tool

        print(f"✅ 工具 {tool.name} 注册成功。")

    
    def register_function(self,name:str,description:str,func:Callable[[str],str]):
        """
        注册函数
        """

        if name in self._functions:
            print(f"⚠️ 函数工具 {name} 已存在,已有工具将被覆盖。")
        
        self._functions[name] = {
            "description": description,
            "function": func
        }

        print(f"✅ 函数工具 {name} 注册成功。")

    def excute_tool(self,name:str,input_text:str)->str:
        """
        执行工具
        """

        if name in self._tools:
            tool = self._tools[name]
            try:
                return tool.run({"input": input_text})
            except Exception as e:
                print(f"工具 {name} 执行出错: {e}")
                return ""

        if name in self._functions:
            func = self._functions[name]["function"]
            try:
                return func(input_text)
            except Exception as e:
                print(f"函数工具 {name} 执行出错: {e}")
                return ""

        else:
            print(f"❌ 未找到工具 {name} 。")
            return "" 
    

    def list_tools(self)->List[str]:
        """
        列出所有工具名称
        """
        return List(self._tools.keys())+List(self._functions.keys())


    def get_tool_description(self)->str:
        """
        获取所有工具描述
        """
        descriptions = []
        for tool in self._tools.values():
            descriptions.append(f"{tool.name}: {tool.description}")
        for name, info in self._functions.items():
            descriptions.append(f"{name}: {info['description']}")
        return "\n".join(descriptions) if descriptions else "无工具可用。"

global_tool_registry = ToolRegistry()