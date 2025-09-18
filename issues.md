# 问题记录日志（FinAgent 项目）

## 1. `ModuleNotFoundError: No module named 'langchain_community'`
- **原因**：langchain 新版本把 `chat_models` 等拆分到了 `langchain_community`。
- **解决方案**：安装 `langchain-community` 包。
- **效果**：问题解决，`test_llm.py` 成功运行。

## 2. DeepSeek 无 Embedding API
- **原因**：DeepSeek 目前只提供 Chat/Completion，缺少向量化接口。
- **解决方案**：切换为 Gemini Embedding 或 OpenAI Embedding。
- **效果**：决定采用 Gemini Embedding。

## 3. `GoogleGenerativeAIError: Timeout of 60.0s exceeded`
- **原因**：国内环境无法直连 Google API。
- **解决方案**：确认需代理访问，或改用其他 Embedding。
- **效果**：暂时保留 Gemini Embedding，准备调整。

## 4. `429 You exceeded your current quota`（配额限制）
- **原因**：Gemini 免费 Embedding 调用次数过多，触发每日/每分钟配额上限。
- **解决方案**：采取 **方案 A（减少 chunk 数量）**，并准备 **方案 C（分批 sleep）**。
- **效果**：成功绕过限制，文档切分 & 向量化完成。
