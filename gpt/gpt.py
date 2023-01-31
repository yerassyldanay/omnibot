import openai,os,sys

prompt = 'Imagine yourself as an expert in copywriting and give answer to the previous question?'
openai.api_key = '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'

completions = openai.Completion.create(
    engine="text-davinci-003",
    prompt=prompt,
    max_tokens=1024,
    n=1,
    stop=None,
    temperature=0.5
)

message = completions.choices[0].text
print(message)
