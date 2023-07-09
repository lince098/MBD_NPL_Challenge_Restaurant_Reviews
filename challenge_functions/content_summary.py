import openai
import os
import asyncio
import logging

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

openai.api_key = os.getenv("OPEN_AI_API_KEY")

GPT_MODEL = "gpt-3.5-turbo"

PROMPT_BEGINNING = """Please analyze this restaurant review and provide a concise summary highlighting its key points:\n"""


async def summarize(selected_list, df):
    if not selected_list:
        return

    selected_rows = df.iloc[selected_list, :]
    selected_rows_list = selected_rows["body"].to_list()

    """This prompt was optimized by ChatGPT with this input (Yes, I've greeted ChatGPT):
        Hi chatgpt, I want you to improve the next prompt im going to send you. To do that, correct mistakes and optimize it so it becomes shorter and cheaper to use: 

        You will receive different reviews of a restaurant. I want you to understand them and make summary that extracts the main points of them
    """

    requests_prompts = [PROMPT_BEGINNING + msg for msg in selected_rows_list]

    responses = await asyncio.gather(
        *[__send_request(prompt) for prompt in requests_prompts]
    )

    logger.debug(responses)
    logger.debug(selected_rows_list)
    return [
        {"Review": msg, "Summary": response}
        for msg, response in zip(selected_rows_list, responses)
    ]


async def __send_request(prompt):
    response = openai.ChatCompletion.create(
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        model=GPT_MODEL,
        temperature=0,
    )

    return response["choices"][0]["message"]["content"]
