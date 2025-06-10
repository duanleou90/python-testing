from quart import Quart, request, jsonify, Response
from openai import OpenAI
import json
import asyncio
import os

app = Quart(__name__)
client = OpenAI(api_key="")


@app.route("/ask", methods=["POST"])
async def ask():
    data = await request.get_json()
    question = data.get("question", "").strip()

    if not question:
        return jsonify({"error": "Question is required"}), 400

    async def generate_stream():
        try:
            # Call OpenAI API with streaming enabled
            stream = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "user", "content": question}
                ],
                stream=True
            )

            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    content = chunk.choices[0].delta.content
                    # Format as Server-Sent Events
                    yield f"data: {json.dumps({'content': content})}\n\n"

            # Send end signal
            yield f"data: {json.dumps({'done': True})}\n\n"

        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return Response(
        generate_stream(),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type'
        }
    )


if __name__ == "__main__":
    app.run()