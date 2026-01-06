# openaiをインポート
import os
from openai import OpenAI
# OpenAI API KEY (環境変数推奨)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
