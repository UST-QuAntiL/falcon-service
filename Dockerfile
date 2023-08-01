FROM ubuntu:22.04

# build ggllm

RUN apt-get update && apt-get install -y git build-essential cmake python3 python3-venv python3-pip curl
RUN mkdir ggllm

WORKDIR /ggllm

RUN git clone https://github.com/cmp-nct/ggllm.cpp.git
WORKDIR ggllm.cpp

RUN git checkout master-f78be9b
RUN mkdir build
WORKDIR build

RUN cmake -DLLAMA_CUBLAS=0 ..
RUN cmake --build . --config Release

# install dependencies for convert script

RUN python3 -m pip install torch==2.0.1 numpy==1.25.1 transformers==4.31.0

# install REST API server

ADD . /app
WORKDIR /app

RUN curl -sSL https://install.python-poetry.org | python3 -
RUN /root/.local/bin/poetry install

CMD /root/.local/bin/poetry run uvicorn main:app --host "0.0.0.0"
