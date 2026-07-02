"""
LNS LLM 客户端 — 对接大模型实现 AI 对话。

当前支持：
  - DeepSeek（deepseek-chat / deepseek-reasoner）
  - DashScope（阿里云通义千问 qwen-max）
  - OpenAI 兼容接口

配置（优先级从高到低）：
  1. DEEPSEEK_API_KEY → DeepSeek
  2. DASHSCOPE_API_KEY → DashScope
  3. OPENAI_API_KEY → OpenAI

使用：
  client = LLMClient()
  response = client.chat(prompt_text)
"""

import json
import os
import time


# ── API Key 自动检测 ─────────────────────────────────────

def _detect_api_key():
    """自动检测可用的 API Key（按优先级）"""
    # 1. DeepSeek
    key = os.environ.get("DEEPSEEK_API_KEY", "")
    if key:
        model = os.environ.get("DEEPSEEK_MODEL", "deepseek-chat")
        base_url = os.environ.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1")
        return {
            "provider": "deepseek",
            "api_key": key,
            "base_url": base_url,
            "model": model,
        }

    # 2. DashScope
    key = os.environ.get("DASHSCOPE_API_KEY", "")
    if key:
        return {
            "provider": "dashscope",
            "api_key": key,
            "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
            "model": "qwen-max",
        }

    # 3. OpenAI
    key = os.environ.get("OPENAI_API_KEY", "")
    if key:
        return {
            "provider": "openai",
            "api_key": key,
            "base_url": os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1"),
            "model": "gpt-4o-mini",
        }

    return None


# ── LLM 客户端 ───────────────────────────────────────────

class LLMClient:
    """
    LLM 客户端 — 对接大模型。

    使用 http.client 实现，零外部依赖。
    """

    def __init__(self, config=None):
        """
        Args:
            config: {
                "provider": "dashscope" | "openai",
                "api_key": "...",
                "base_url": "...",
                "model": "qwen-max" | "gpt-4o-mini",
            }
            不传则自动检测环境变量。
        """
        if config is None:
            config = _detect_api_key()

        if config is None:
            raise ValueError(
                "未找到 API Key。请设置 DASHSCOPE_API_KEY 或 OPENAI_API_KEY 环境变量。"
            )

        self.config = config
        self._validate_config()

    def _validate_config(self):
        required = ["api_key", "base_url", "model"]
        for r in required:
            if not self.config.get(r):
                raise ValueError(f"LLM 配置缺少 {r}")

    def chat(self, prompt_text, system_prompt=None, temperature=0.7, max_tokens=1024):
        """
        发送 Prompt 到 LLM 并获取响应。

        Args:
            prompt_text: 用户输入的完整 Prompt
            system_prompt: 系统提示词（覆盖 Prompt Engine 的 system prompt）
            temperature: 生成温度 (0-1)，越低越确定
            max_tokens: 最大生成长度

        Returns: {
            "success": bool,
            "content": str,        AI 回复内容
            "finish_reason": str,
            "usage": dict,          tokens 用量
            "error": str,          失败原因
        }
        """
        if system_prompt is None:
            system_prompt = self._default_system_prompt()

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt_text},
        ]

        return self._call_api(messages, temperature, max_tokens)

    def chat_multi_turn(self, messages, temperature=0.7, max_tokens=1024):
        """
        多轮对话。

        Args:
            messages: [{"role": "system"/"user"/"assistant", "content": "..."}, ...]
            temperature: 生成温度
            max_tokens: 最大生成长度

        Returns: 同 chat()
        """
        return self._call_api(messages, temperature, max_tokens)

    def _default_system_prompt(self):
        """默认系统提示词"""
        return (
            "You are Life Navigation AI, a structured decision navigation system. "
            "You are NOT a fortune teller. Never predict the future. "
            "Always base your answers on the structured data provided. "
            "Use modern language, never 命理/mystical terms. "
            "Output in Chinese unless the user asks otherwise."
        )

    def _call_api(self, messages, temperature, max_tokens):
        """调用大模型 API"""
        provider = self.config["provider"]
        if provider == "deepseek":
            return self._call_openai(messages, temperature, max_tokens)  # DeepSeek 兼容 OpenAI 接口
        elif provider == "dashscope":
            return self._call_dashscope(messages, temperature, max_tokens)
        elif provider == "openai":
            return self._call_openai(messages, temperature, max_tokens)
        else:
            return {"success": False, "error": f"不支持的 provider: {provider}"}

    def _call_dashscope(self, messages, temperature, max_tokens):
        """调用 DashScope API"""
        import http.client
        import urllib.parse

        url = urllib.parse.urlparse(self.config["base_url"])
        conn = http.client.HTTPSConnection(url.hostname, url.port or 443, timeout=30)

        body = {
            "model": self.config["model"],
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        headers = {
            "Authorization": f"Bearer {self.config['api_key']}",
            "Content-Type": "application/json",
        }

        path = url.path + "/chat/completions" if url.path else "/v1/chat/completions"

        try:
            conn.request("POST", path, json.dumps(body), headers)
            resp = conn.getresponse()
            data = json.loads(resp.read().decode())
            conn.close()

            if resp.status != 200:
                error_msg = data.get("error", {}).get("message", str(data))
                return {"success": False, "error": error_msg}

            choice = data["choices"][0]
            return {
                "success": True,
                "content": choice["message"]["content"],
                "finish_reason": choice.get("finish_reason", "stop"),
                "usage": data.get("usage", {}),
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _call_openai(self, messages, temperature, max_tokens):
        """调用 OpenAI 兼容 API"""
        import http.client
        import urllib.parse

        url = urllib.parse.urlparse(self.config["base_url"])
        conn = http.client.HTTPSConnection(url.hostname, url.port or 443, timeout=30)

        body = {
            "model": self.config["model"],
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        headers = {
            "Authorization": f"Bearer {self.config['api_key']}",
            "Content-Type": "application/json",
        }

        path = url.path + "/chat/completions" if url.path else "/v1/chat/completions"

        try:
            conn.request("POST", path, json.dumps(body), headers)
            resp = conn.getresponse()
            data = json.loads(resp.read().decode())
            conn.close()

            if resp.status != 200:
                error_msg = data.get("error", {}).get("message", str(data))
                return {"success": False, "error": error_msg}

            choice = data["choices"][0]
            return {
                "success": True,
                "content": choice["message"]["content"],
                "finish_reason": choice.get("finish_reason", "stop"),
                "usage": data.get("usage", {}),
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def __repr__(self):
        return f"LLMClient(provider={self.config['provider']}, model={self.config['model']})"
