import openai

openai.api_key = ""
message = "MLOps에 대해 설명해줘"

if __name__ == "__main__":
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "user",
                "content": message,
            }
        ],
    )
    print(completion.choices[0].message.content)
