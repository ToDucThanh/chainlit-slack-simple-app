import re

import chainlit as cl
import ollama
from scrapegraphai.graphs import SmartScraperGraph


@cl.on_chat_start
async def start():
    graph_config = {
        "llm": {
            "model": "ollama/llama3",
            "temperature": 0,
            "format": "json",
            "base_url": "http://localhost:11434",
        },
        "embeddings": {
            "model": "ollama/nomic-embed-text",
            "base_url": "http://localhost:11434",
        },
        "verbose": True,
    }
    cl.user_session.set("graph_config", graph_config)


@cl.on_message
async def on_message(message: cl.Message):
    if "https" in message.content:
        graph_config = cl.user_session.get("graph_config")
        link = re.findall("https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+", message.content)
        link = link[0]
        question = re.search(r"(.+?)\bSource\b", message.content)
        question = question.group(1)
        smart_scraper_graph = SmartScraperGraph(
            prompt=question,
            source=link,
            config=graph_config,
        )
        result = smart_scraper_graph.run()
    else:
        response = ollama.chat(
            model="llama3",
            messages=[
                {"role": "user", "content": message.content},
            ],
        )
        result = response["message"]["content"]

    await cl.Message(content=result).send()
