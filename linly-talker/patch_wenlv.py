# -*- coding: utf-8 -*-
"""
远程补丁脚本:把文旅讲解员接入 Linly-Talker
在服务器上执行,对 LLM/__init__.py 和 webui.py 做精确文本替换,每处校验。
"""
import shutil, sys

BASE = '/root/autodl-tmp/Linly-Talker'

def patch(path, replacements):
    with open(path, 'r', encoding='utf-8') as f:
        src = f.read()
    shutil.copy(path, path + '.bak_wenlv')  # 备份
    for old, new in replacements:
        if new in src and old not in src:
            print(f"  [跳过] {path}: 已打过补丁 -> {new[:30]}...")
            continue
        if old not in src:
            print(f"  [失败] {path}: 找不到目标文本 -> {old[:50]}...")
            sys.exit(1)
        src = src.replace(old, new, 1)
        print(f"  [OK] {path}: {old[:40]!r} -> {new[:40]!r}")
    with open(path, 'w', encoding='utf-8') as f:
        f.write(src)

print("== 1. LLM/__init__.py: 注册 DeepSeek ==")
patch(f'{BASE}/LLM/__init__.py', [
    ("from .ChatGPT import ChatGPT",
     "from .ChatGPT import ChatGPT\nfrom .DeepSeek import DeepSeek"),
    ("if model_name not in ['Linly', 'Qwen', 'Qwen2', 'Gemini', 'ChatGLM', 'ChatGPT', 'Llama2Chinese', 'GPT4Free', 'QAnything', '直接回复 Direct Reply']:\n            raise ValueError(\"model_name must be one of ['Linly', 'Qwen', 'Qwen2', 'Gemini', 'ChatGLM', 'ChatGPT', 'Llama2Chinese', 'GPT4Free', 'QAnything', '直接回复 Direct Reply']\")",
     "if model_name not in ['Linly', 'Qwen', 'Qwen2', 'Gemini', 'ChatGLM', 'ChatGPT', 'DeepSeek', 'Llama2Chinese', 'GPT4Free', 'QAnything', '直接回复 Direct Reply']:\n            raise ValueError(\"model_name must be one of ['Linly', 'Qwen', 'Qwen2', 'Gemini', 'ChatGLM', 'ChatGPT', 'DeepSeek', 'Llama2Chinese', 'GPT4Free', 'QAnything', '直接回复 Direct Reply']\")"),
    ("elif model_name == 'ChatGLM':\n            llm = ChatGLM(self.mode, model_path)",
     "elif model_name == 'DeepSeek':\n            llm = DeepSeek(model_path or None, api_key)\n        elif model_name == 'ChatGLM':\n            llm = ChatGLM(self.mode, model_path)"),
])

print("== 2. webui.py: 文旅人设 + DeepSeek 选项 ==")
patch(f'{BASE}/webui.py', [
    # 2a. 全局人设:通用助手 -> 故宫讲解员(带降级保护)
    ("DEFAULT_SYSTEM = '你是一个很有帮助的助手'",
     "try:\n    from wenlv_config import SCENIC_SYSTEM_PROMPT as DEFAULT_SYSTEM\nexcept Exception:\n    DEFAULT_SYSTEM = '你是故宫博物院的金牌讲解员小宫,热情亲和,回答控制在80字以内'"),
    # 2b. LLM 下拉框加 DeepSeek 选项
    ("choices=['Qwen', 'Qwen2', 'Linly', 'Gemini', 'ChatGLM', 'ChatGPT', 'GPT4Free', 'QAnything', '直接回复 Direct Reply', 'Comming Soon!!!'], value='直接回复 Direct Reply'",
     "choices=['Qwen', 'Qwen2', 'Linly', 'Gemini', 'ChatGLM', 'ChatGPT', 'DeepSeek', 'GPT4Free', 'QAnything', '直接回复 Direct Reply', 'Comming Soon!!!'], value='直接回复 Direct Reply'"),
    # 2c. 模型加载分支
    ("elif model_name == '直接回复 Direct Reply':\n            llm = llm_class.init_model(model_name)\n            gr.Info(\"直接回复，不使用LLM模型\")",
     "elif model_name == 'DeepSeek':\n            llm = llm_class.init_model('DeepSeek', api_key=openai_apikey)\n            gr.Info(\"DeepSeek文旅讲解员已就绪（未配置密钥时自动使用知识库兜底）\")\n        elif model_name == '直接回复 Direct Reply':\n            llm = llm_class.init_model(model_name)\n            gr.Info(\"直接回复，不使用LLM模型\")"),
    # 2d. 界面标题改成文旅导览
    ("def get_title(title = 'Linly 智能对话系统 (Linly-Talker)'):",
     "def get_title(title = '故宫博物院 · 智能讲解数字人 (文旅导览)'):"),
])

print("== 补丁完成,备份文件: *.bak_wenlv ==")
