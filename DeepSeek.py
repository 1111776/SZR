# -*- coding: utf-8 -*-
"""全国景点讲解员。每次提问带上游客选的地点，不把不同景点的对话混在一起。"""
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from wenlv_config import (
        DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL, DEEPSEEK_MODEL,
        build_system_prompt, get_fallback_answer,
    )
except ImportError:
    DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY", "")
    DEEPSEEK_BASE_URL = "https://api.deepseek.com"
    DEEPSEEK_MODEL = "deepseek-chat"

    def build_system_prompt(place=""):
        return "你是文旅讲解员阿青。" + (f"游客要去{place}。" if place else "")

    def get_fallback_answer(q, place=""):
        return "抱歉，我暂时回答不了这个问题。"

_GENERIC_SYSTEMS = {"", "system无效", "你是一个很有帮助的助手"}


class DeepSeek():
    def __init__(self, model_path=None, api_key=None, prefix_prompt=""):
        self.model_path = model_path or DEEPSEEK_MODEL
        self.api_key = api_key or DEEPSEEK_API_KEY
        self.prefix_prompt = prefix_prompt
        self.system_prompt = build_system_prompt("")
        self.history = []
        self.client = None
        if self.api_key:
            try:
                from openai import OpenAI
                self.client = OpenAI(api_key=self.api_key, base_url=DEEPSEEK_BASE_URL)
                print("DeepSeek 文旅讲解员初始化成功 (API模式)")
            except Exception as e:
                print("DeepSeek client初始化失败:", e)
        else:
            print("未配置 DEEPSEEK_API_KEY")

    def generate(self, message, system_prompt="", place=""):
        if system_prompt in _GENERIC_SYSTEMS:
            system_prompt = build_system_prompt(place)
        if self.client is not None:
            try:
                response = self.client.chat.completions.create(
                    model=self.model_path,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": message},
                    ],
                    temperature=0.7,
                    max_tokens=160,
                )
                return response.choices[0].message.content.strip()
            except Exception as e:
                print("DeepSeek API调用失败:", e)
        return get_fallback_answer(message, place)

    def chat(self, system_prompt, message, history):
        response = self.generate(message, system_prompt)
        history.append((message, response))
        return response, history
