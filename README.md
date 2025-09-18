FinAgent - 智能投资研究助手
📌 项目简介

FinAgent 是一个基于 LangChain + Chroma + 阿里云百炼（DashScope） 的企业级 RAG 智能体。
它能够处理财报、研报 PDF，支持自然语言查询和多轮问答，辅助投资研究人员快速获取关键信息，提升研究效率。

⚙️ 技术栈

编程语言: Python 3.10

框架: LangChain, LangGraph (规划中)

向量数据库: ChromaDB

大模型服务: 阿里云百炼 Qwen + text-embedding-v4

Web 应用: FastAPI / Streamlit (可扩展为前端交互)

🚀 功能特性

📂 文档管理：自动解析 PDF（年报、半年报、研报）并切分成语义片段

🔍 RAG 检索：基于向量数据库的精准问答

🧠 上下文记忆：支持多轮追问（例如“研发投入是多少？”→“那比去年增长多少？”）

📑 可追溯回答：每个答案都附带来源文档片段，确保透明与可信度

💡 企业级扩展：可集成行情 API、数据库等外部工具

🛠️ 快速开始
1. 克隆仓库
git clone https://github.com/你的用户名/finagent.git
cd finagent

2. 安装依赖
pip install -r requirements.txt

3. 配置环境变量

在根目录创建 .env 文件，内容如下：

DASHSCOPE_API_KEY=你的阿里云百炼APIKey

4. 构建向量数据库

把 PDF 文件放到 data/ 文件夹下，然后运行：

python ingest.py

5. 测试问答
python search_test.py


示例输入：

问题: 中芯国际的利润总额是多少？

📂 项目结构
finagent/
│── data/                  # 存放 PDF 文档
│── db/                    # 向量数据库 (Chroma 持久化目录)
│── ingest.py              # 数据处理 & 向量化脚本
│── search_test.py         # 问答测试脚本
│── config.py              # API Key & 模型配置
│── requirements.txt       # 依赖
│── README.md              # 项目说明文档
│── .gitignore             # 忽略文件

🔮 下一步优化

 接入 LangGraph，实现对话级记忆和多分支逻辑

 增加 FastAPI/Streamlit 前端，支持交互式查询

 集成 实时行情 & 数据库工具，扩展企业级应用场景
