import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

def quesiton_llm(question, llm_model) -> requests.Response:
        response: requests.Response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {os.environ['OPENROUTER_API_KEY']}",
            },
            data=json.dumps(
                {
                    "model": llm_model,
                    "messages": question['input'],
                }
            ),
        )
        response.raise_for_status()
        data = response.json()
        answer = data["choices"][0]["message"]['content']
        print(answer)
        return 1 if question['ideal'] in answer else 0


question ={'input': [{'role': 'system', 'content': 'You are an expert mariner and navigator.'}, {'role': 'user', 'content': "Nautical situation: The own ship, called 'BASTO VI', is a 122.0 meters long Passenger/Ro-Ro Cargo Ship moving at a speed of 10.0 knots on a course of 0.0 degrees. Around the own ship there are 6 target ships. Target 1, 'GOO', a Passenger/Ro-Ro Cargo Ship of 178.0 meters, making 12.0 knots on a course of 180.0°. Target ship 1 lies 0.6 nautical miles off, bearing 16.7° relative. Target 2, 'FOO', a Fishing of 178.0 meters, making 12.0 knots on a course of 180.0°. Target ship 2 lies 0.2 nautical miles off, bearing 270.0° relative. Target 3, 'BAR', a General Cargo Ship of 178.0 meters, making 12.0 knots on a course of 180.0°. Target ship 3 lies 0.5 nautical miles off, bearing 180.0° relative. Target 4, 'BAR', a General Cargo Ship of 178.0 meters, making 10.0 knots on a course of 270.0°. Target ship 4 lies 0.6 nautical miles off, bearing 63.4° relative. Target 5, 'BAR', a General Cargo Ship of 178.0 meters, making 10.0 knots on a course of 270.0°. Target ship 5 lies 1.0 nautical miles off, bearing 270.0° relative. Target 6, 'BAR', a General Cargo Ship of 178.0 meters, making 10.0 knots on a course of 270.0°. Target ship 6 lies 0.8 nautical miles off, bearing 45.0° relative. Question: On which side of the own ship is the target ship 6? Answer only either 'starboard', 'portside', or 'neither'."}], 'ideal': 'starboard'}
point = quesiton_llm(question,'openai/gpt-3.5-turbo-16k')
print(point)