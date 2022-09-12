import numpy as np
import re
import os
import openai
from time import time,sleep
import textwrap
from random import seed,choice


def open_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as infile:
        return infile.read()


def save_file(filepath, content):
    with open(filepath, 'w', encoding='utf-8') as outfile:
        outfile.write(content)


openai.api_key = open_file('openaiapikey.txt')
workingdir = 'experiment3/'
logdir = 'experiment3_logs/'
#agent_model = 'agent_model_COF.txt'
#agent_model = 'agent_model_FFA.txt'
agent_model = 'agent_model_null.txt'
gpt3_model = 'davinci'


def gpt3_completion(prompt, label='gpt3', engine='davinci', temp=0.7, top_p=1.0, tokens=1000, freq_pen=0.0, pres_pen=0.0, stop=['asdfasdf', 'asdasdf']):
    max_retry = 5
    retry = 0
    prompt = prompt.encode(encoding='ASCII',errors='ignore').decode()  # force it to fix any unicode errors
    while True:
        try:
            response = openai.Completion.create(
                engine=engine,
                prompt=prompt,
                temperature=temp,
                max_tokens=tokens,
                top_p=top_p,
                frequency_penalty=freq_pen,
                presence_penalty=pres_pen,
                stop=stop)
            text = response['choices'][0]['text'].strip()
            text = re.sub('\s+', ' ', text)
            filename = '%s_%s.txt' % (time(), label)
            save_file('%s%s' % (logdir, filename), prompt + '\n\n==========\n\n' + text)
            return text
        except Exception as oops:
            retry += 1
            if retry >= max_retry:
                return "GPT3 error: %s" % oops
            print('Error communicating with OpenAI:', oops)
            sleep(1)


def load_story():
    files = os.listdir(workingdir)
    result = list()
    for file in files:
        result.append(open_file('%s%s' % (workingdir, file)).strip())
    return result


def summarize_block(text_block):
    chunks = textwrap.wrap(text_block, 2000)
    result = list()
    #print(len(chunks), 'chunks to summarize')
    for chunk in chunks:
        prompt = open_file('prompt_summary.txt').replace('<<SUMMARY>>', chunk)
        summary = gpt3_completion(prompt, label='summary', engine='text-davinci-002')
        result.append(summary)
    summary = '. '.join(result).replace('..','.')
    return summary


def recursively_summarize(story):
    #print('Recursively summarizing story up to this point...')
    summary = '\n'.join(story).strip()
    while True:
        if len(summary) < 1000:
            return summary
        summary = summarize_block(summary)


def get_recent(story):
    if len(story) <= 10:  # increase this number to get bigger chunks of story
        return '\n'.join(story)
    else:
        return '\n'.join(story[-10:])  # increase this number to get bigger chunks of story


if __name__ == '__main__':
    for i in list(range(0, 20)):
        story = load_story()
        print('\n\nSummarizing...')
        summary = recursively_summarize(story)
        print('\n\nSummary:', summary)
        prompt = open_file(agent_model) + '\n\n%s\n\nThe following are my thoughts:' % summary
        print('\n\nPrompt:', prompt)
        completion = gpt3_completion(prompt, label='thought', engine=gpt3_model, tokens=256)
        print('\n\nCompletion:', completion)
        filename = 'log_%s.txt' % time()
        save_file(workingdir + filename, completion)