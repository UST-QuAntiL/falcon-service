"""
Copyright 2023 University of Stuttgart

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""
import os
import subprocess
from enum import Enum
from typing import List

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


class Role(Enum):
    user = "user"
    assistant = "assistant"


class Message(BaseModel):
    role: Role
    text: str


class Chat(BaseModel):
    messages: List[Message]


@app.post("/chat")
async def generate_chat_response(chat: Chat) -> Chat:
    result = subprocess.run(
        [
            "/ggllm/ggllm.cpp/build/bin/falcon_main",
            "-m", f"/models/{os.environ['MODEL_FILE']}",
            "-p",
            convert_chat_to_prompt(chat)
        ],
        capture_output=True)

    llm_output: str = result.stdout.decode()

    return convert_llm_output_to_chat(llm_output)


def convert_chat_to_prompt(chat: Chat) -> str:
    prompt = ""

    for message in chat.messages:
        if message.role == Role.user:
            prompt += f"<|prompter|>{message.text}<|endoftext|>"
        elif message.role == Role.assistant:
            prompt += f"<|assistant|>{message.text}<|endoftext|>"
        else:
            raise ValueError(f"unknown role {message.role}")

    return prompt + "<|assistant|>"


def convert_llm_output_to_chat(output: str) -> Chat:
    messages = output.split("<|endoftext|>")
    chat = Chat(messages=[])

    for message in messages:
        if message.startswith("<|prompter|>"):
            chat.messages.append(Message(role=Role.user, text=message[12:]))
        elif message.startswith("<|assistant|>"):
            chat.messages.append(Message(role=Role.assistant, text=message[13:]))
        elif message == "":
            pass
        else:
            raise ValueError(f"Message doesn't start with valid role: {message}")

    return chat
