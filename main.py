import os
import json
import re
from gpt4all import GPT4All
from personality import get_system_prompt

MODEL_PATH = r"C:\Users\Owner\Documents\Project\Main\ON!X\models\phi-2.Q4_K_M(4).gguf"
MEMORY_FILE = r"C:\Users\Owner\Documents\Project\Main\ON!X\memory.json"

# Initialize model
if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError("Model file not found. Check the path.")

model = GPT4All(MODEL_PATH, allow_download=False)

# Load memory
if os.path.exists(MEMORY_FILE):
    with open(MEMORY_FILE, "r", encoding="utf-8") as f:
        memory_data = json.load(f)
else:
    memory_data = {"facts": {"name": "ON!X", "creator": "Richard Andrew", "user": "Richard"}, "conversations": []}

print("ON!X is online. Type 'quit' to exit.\n")

# Chat Loop
while True:
    user_input = input("You: ").strip()
    if user_input.lower() == 'quit':
        print("ON!X: Always a pleasure, Richard. I'll be here when you need me.")
        break

    # Get recent conversation history
    recent_history = memory_data["conversations"][-4:] if memory_data["conversations"] else []
    history_text = ""
    for msg in recent_history:
        role = "Human" if msg["role"] == "user" else "ON!X"
        history_text += f"{role}: {msg['content']}\n"

    # Build the complete prompt using imported system prompt
    system_prompt = get_system_prompt()
    complete_prompt = f"{system_prompt}\n{history_text}Human: {user_input}\nON!X:"

    # Generate response
    try:
        response = model.generate(
            complete_prompt,
            max_tokens=80,  # Reduced to prevent overflow
            temp=0.5,       # Lower temperature for more focused responses
            top_k=30,
            top_p=0.8,
            repeat_penalty=1.3
        )

        # --- IMPROVED CLEANING ---
        # Remove everything after common continuation patterns
        response = response.split("Human:")[0].strip()
        response = response.split("###")[0].strip()
        
        # Remove exercise/instruction patterns
        stop_patterns = [
            "##Your task:", "## Exercise", "Exercise 1:", "Your task:",
            "**Rewrite**", "SAT exam", "knowledge exercises",
            "### END", "### END OF EXAMPLES", "Human:"
        ]
        
        for pattern in stop_patterns:
            response = response.split(pattern)[0].strip()
        
        # Remove ON!X: prefix if present
        response = re.sub(r'^ON!X:\s*', '', response)
        
        # Remove any special symbols and HTML tags
        response = re.sub(r'<[^>]*>', '', response)
        response = re.sub(r'[♥❤️♡]', '', response)
        response = re.sub(r'##+.*', '', response)  # Remove ## headings
        response = re.sub(r'\*\*.*?\*\*', '', response)  # Remove **bold** text
        
        # Clean up any extra whitespace
        response = re.sub(r'\s+', ' ', response).strip()
        
        # Ensure proper sentence ending - stop at first complete thought
        sentences = re.split(r'[.!?]', response)
        if len(sentences) > 1:
            response = sentences[0] + '.'  # Take only first sentence
        elif response and not response.endswith(('.', '!', '?')):
            response = response.rstrip(' ,') + '.'
        
        # Final safety check - if response seems to start new content, truncate
        if any(word in response.lower() for word in ['exercise', 'rewrite', 'sat', 'task:', '##']):
            # Find where the natural response ends and garbage starts
            response = re.split(r'[.!?]', response)[0] + '.'
        
        if not response or len(response) < 2:
            response = "Hey Richard! Good to hear from you."

        print(f"ON!X: {response}")

        # Save to memory
        memory_data["conversations"].append({"role": "user", "content": user_input})
        memory_data["conversations"].append({"role": "onx", "content": response})

        with open(MEMORY_FILE, "w", encoding="utf-8") as f:
            json.dump(memory_data, f, ensure_ascii=False, indent=4)

    except Exception as e:
        print(f"ON!X: Sorry Richard, I encountered an error: {e}")