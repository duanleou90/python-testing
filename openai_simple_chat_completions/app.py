from quart import Quart, request, jsonify
from openai import OpenAI
import os

app = Quart(__name__)

client = OpenAI(api_key="")

@app.route("/ask", methods=["POST"])
async def ask():
    data = await request.get_json()

    question = data.get("question", "").strip()
    if not question:
        return jsonify({"error": "Question is required"}), 400

    try:
        # Call OpenAI API
        response = client.chat.completions.create(
            model="gpt-4o",  # or gpt-4 if available
            messages=[
                {"role": "user", "content": question}
            ]
        )
        answer = response.choices[0].message.content.strip()
        return jsonify({"answer": answer})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run()
