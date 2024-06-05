import os

import torch
import transformers

import dotenv
from openai import OpenAI
from retry import retry

dotenv.load_dotenv()
client = OpenAI()
pipeline = None
groq_client = None


@retry(exceptions=Exception, tries=5, delay=10, backoff=2)
def call_chatbot(messages: list, model="gpt35", n=1):
    if "gpt" in model:
        model = {"gpt4o": "gpt-4o", "gpt4": "gpt-4-turbo", "gpt35": "gpt-3.5-turbo"}[model]
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": message} for message in messages],
            n=n
        )
        return [response.choices[i].message.content for i in range(n)]
    elif "llama" in model:
        global pipeline
        model_id = {"llama3-8B": "meta-llama/Meta-Llama-3-8B-Instruct", "llama3-70B": "meta-llama/Meta-Llama-3-70B-Instruct"}[model]
        if pipeline is None:
            pipeline = transformers.pipeline(
                "text-generation",
                model=model_id,
                model_kwargs={"torch_dtype": torch.bfloat16},
                device_map="auto",
            )
        prompt = pipeline.tokenizer.apply_chat_template(
            [{"role": "user", "content": message} for message in messages],
            tokenize=False,
            add_generation_prompt=True,
        )

        terminators = [
            pipeline.tokenizer.eos_token_id,
            pipeline.tokenizer.convert_tokens_to_ids("<|eot_id|>")
        ]

        responses = pipeline(
            prompt,
            max_new_tokens=256,
            eos_token_id=terminators,
            do_sample=True,
            temperature=0.6,
            top_p=0.9,
            num_return_sequences=n,
        )
        responses = [response["generated_text"][len(prompt):] for response in responses]
        print(responses)
        return responses
    elif "groq3" in model:
        model_id = {"groq3-8B": "llama3-8b-8192", "groq3-70B": "llama3-70b-8192"}[model]
        from groq import Groq
        global groq_client
        if groq_client is None:
            groq_client = Groq(
                api_key=os.environ.get("GROQ_API_KEY"),
            )
        responses = []
        for i in range(n):
            chat_completion = groq_client.chat.completions.create(
                messages=[{"role": "user", "content": message} for message in messages],
                model=model_id,
                n=1,
            )
            responses.append(chat_completion.choices[0].message.content)
        print(responses)
        return responses
    else:
        raise NotImplementedError


def ask_true_or_false(prompt, model) -> str:
    response = ""
    for i in range(3):
        response = call_chatbot([prompt], model=model, n=1)[0]
        if "True" in response:
            return "True"
        elif "False" in response:
            return "False"
    print(f"The prompt: `{prompt}` failed to respond with True or False.")
    return response


def ask_list(prompt, model) -> str:
    response = ""
    for i in range(3):
        response = call_chatbot([prompt], model=model, n=1)[0]
        if response.startswith("[") and response.endswith("]"):
            return response
    print(f"The prompt: `{prompt}` failed to respond with a list.")
    return response


def ask_chatbot(prompt, return_type="str", model="gpt35") -> str:
    if return_type == "str":
        return call_chatbot([prompt], model=model, n=1)[0]
    elif return_type == "bool":
        return ask_true_or_false(prompt, model=model)
    elif isinstance(return_type, list):
        return ask_list(prompt, model=model)
    else:
        raise NotImplementedError
