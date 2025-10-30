from gpt4all import GPT4All
from personality import get_persona
import os

# absolute path to your model file
model_path = r"C:\Users\Owner\Documents\Project\Main\ON!X\models\tinyllama-1.1b-chat-v1.0.Q2_K.gguf"

# make sure it exists
if not os.path.exists(model_path):
    raise FileNotFoundError("Model file not found. Check the path.")

# initialize model without trying to download anything
model = GPT4All(model_path, allow_download=False)

# Load the personality
persona = get_persona()

# Memory list to store conversation history
memory = []

# Initiate loop so you can talk to her
while True:
    user_input = input("You: ")
    if user_input.lower() == 'quit':
        print("ON!X Shutting down.")
        break

    # Combine personality
    prompt = f"{persona}\n\n--- Conversation ---\n"
    if memory:
        prompt += "\n".join(memory[-3:]) + "\n"
    prompt += f"User: {user_input}\nON!X (respond only as yourself, do not invent facts or mention the internet):"



    # Generate a response
    response = model.generate(prompt, max_tokens=80, temp=0.2, top_k=40)

    # Clean output manually
    for token in ["User:", "ON!X:"]:
        if token in response:
            response = response.split(token)[0]

    response = response.strip()


    # print Ai reply
    print("ON!X: ", response.strip())

    # Save last exchange in memory
    memory.append(f"User: {user_input}")
    memory.append(f"ON!X: {response.strip()}")

