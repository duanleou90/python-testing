from quart import Quart, request, Response, jsonify
from openai import OpenAI
import json
import asyncio
from typing import AsyncGenerator

app = Quart(__name__)

# Initialize OpenAI client
client = OpenAI(
    api_key="")


async def stream_openai_response(prompt: str, model: str = "o4-mini", effort: str = "medium") -> AsyncGenerator[
    str, None]:
    """Stream OpenAI response events as Server-Sent Events"""
    try:
        # Create streaming response
        stream = client.responses.create(
            model=model,
            input=prompt,
            reasoning={"effort": effort, "summary": "auto"},
            stream=True
        )

        # Process each event in the stream
        for event in stream:
            event_data = event.model_dump()

            # Format as Server-Sent Event
            sse_data = f"data: {json.dumps(event_data)}\n\n"
            yield sse_data

    except Exception as e:
        error_data = {
            "type": "error",
            "error": str(e),
            "message": "An error occurred while streaming the response"
        }
        yield f"data: {json.dumps(error_data)}\n\n"

    # Send completion event
    completion_data = {"type": "stream_complete"}
    yield f"data: {json.dumps(completion_data)}\n\n"


@app.route('/stream', methods=['POST'])
async def stream_response():
    """Stream OpenAI response for a given prompt"""
    try:
        data = await request.get_json()

        if not data or 'prompt' not in data:
            return jsonify({"error": "Missing 'prompt' in request body"}), 400

        prompt = data['prompt']
        model = data.get('model', 'o4-mini')
        effort = data.get('effort', 'medium')

        return Response(
            stream_openai_response(prompt, model, effort),
            mimetype='text/event-stream',
            headers={
                'Cache-Control': 'no-cache',
                'Connection': 'keep-alive',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
            }
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)