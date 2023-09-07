# langchain_poc

## Scope

- 4 arkivguider som finns i pdf-format (mer manuell parsing hinner vi inte)

  - Kan va värt att testa https://facebookresearch.github.io/nougat/
  - Detta behövs ytterliggare resurser för att utföra, då denna process är “dyr”

- Conversational QA-chain (chatbot) mot dessa arkivguider

  - Utforska olika chain-tekniker
    - Exempelvis så gjorde Peter en “pre-processing” och formulerade frågorna att bli mer “standardiserade”
  - promp-engineering
  - meomerybuffer
  - compressor?

- För att produktifera behöver vi:

  - Docker (helst compose)
  - Rest API (Fast API)
  - Någon form av databas (Chroma DB eller weaviate)
  - Hårdvara för modeller (om vi vill ha on-prem)

- Enkelt användargränssnitt för att göra enkla tester.

  - Gradio

- Feedback loops

  - Strategi för hur vi ska “förbättrar” flödet med feedback
    - callbacks
    - label-studio
    - Involvera annoterare

- Systematisk evaluering av alternativa lösningar, t.ex. open-source (llama 2, cohere) kontra Open-AI

  - Både för embeddings (retrieval) och LLM (augmented generation)
  - Ragas https://github.com/explodinggradients/ragas/blob/main/docs/metrics.md
  - minst 30 frågor måste tas fram. Helst sampled från olika ställen
    - Samma struktur som detta: https://huggingface.co/datasets/explodinggradients/fiqa/viewer/ragas_eval/baseline?row=0
    - Detta behövs ytterligare resurser för att utföra, då denna process är “dyr”

- Active solutions bidrag
  - Om vi fortsätter arbeta med dem, så är vi intresserade av någon som kan främst hantera frontend och backend bitar som berör användargränssnitt och integrering mot våra system
    - Isåfall Peter som kan både React.js och DotNet.
   
Intresting pocs to consider:

https://github.com/hwchase17/conversation-qa-gradio/blob/master/app.py
https://github.com/hwchase17/conversational-retrieval-agent/blob/master/streamlit.py
https://github.com/hwchase17/chat-your-data/blob/master/query_data.py
https://github.com/HumanSignal/label-studio-examples/blob/master/question-answering-system/chatbot.py
https://www.youtube.com/watch?v=iFvCZD4iS2w
https://github.com/FrancescoSaverioZuppichini/gradioGPT/blob/main/src/app.py
course of intreset:
https://learn.mlops.community/courses/llms/introduction-to-qa-systems-with-large-language-models-llms/
