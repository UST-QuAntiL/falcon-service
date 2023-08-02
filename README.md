# Falcon LLM ggml REST API wrapper

This repository contains a REST API wrapper for [Falcon](https://huggingface.co/tiiuae/falcon-7b) models in the [ggml](https://github.com/ggerganov/ggml) format.
It uses [ggllm.cpp](https://github.com/cmp-nct/ggllm.cpp) to execute the models.

## Building the docker image

Build the docker image with: `docker compose build`

## Model conversion / quantization

To convert a Falcon model to the ggml format use the following command.

⚠️ Warning:
- the output model will use 32-bit floats and might therefore be bigger than the input model
- you need to assign enough RAM to docker e.g. for the OpenAssistant Falcon 40B model you need to assign at least 16GB

```
docker run -it --rm -v <local_falcon_model_folder>:/models -v <local_output_folder>:/model_output ggllm python3 /ggllm/ggllm.cpp/falcon_convert.py /models /model_output use-f32
```

To quantize the ggml formatted model, put the `tokenizer.json` file in `<local_output_folder>`.
Use the following command to do 2-bit quantization.
For other quantization options, run the `falcon_quantize` program without arguments.

```
docker run -it --rm -v <local_ggml_model_folder>:/model_output ggllm /ggllm/ggllm.cpp/build/bin/falcon_quantize /model_output/<ggml_model_file> /model_output/model-quant.bin Q2_K
```

## Serving a model as REST API

Create a `.env` file and define the following variables in it:
- MODEL_FOLDER: the absolute path to the folder that contains your ggml model
- MODEL_FILE: the file name of your ggml model

Start the docker compose with `docker compose up`

⚠️ Warning: You need to assign enough RAM to docker.
At least the size of the model file plus 20%.

## Using the REST API

The API is available under http://localhost:8000, the Swagger-UI under http://localhost:8000/docs and the ReDoc UI under http://localhost:8000/redoc. 

The first call to the API can take a minute or more depending on the size of the model.
The next calls will be faster, because the model is already in memory.
