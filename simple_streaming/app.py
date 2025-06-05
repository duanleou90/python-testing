from quart import Quart, Response
import asyncio

app = Quart(__name__)

# The long text to be streamed
TEXT = """
The Xiaomi 16 is expected to be unveiled in China at the end of September, and it's already been rumored to sport a humongous battery. At one point we heard 6,800 mAh, then another rumor just said "over 6,500 mAh".

So, if you've been wondering about the exact capacity of the Xiaomi 16's battery, a new rumor out of China today purportedly brings us the answer: 7,000 mAh. And the phone will have a 6.3x-inch display (so 6.3" to 6.39").

This would be a huge jump in battery capacity from the Xiaomi 15's 5,240 mAh cell, if true, and should make its successor even more appealing from this point of view.

The Xiaomi 16 has also been rumored to sport a flat OLED display, the Snapdragon 8 Elite 2 chipset at the helm, and three 50 MP rear cameras (including a main one with a 1/1.3" type sensor and possibly a periscope telephoto).
"""

# Split the text into words
WORDS = TEXT.strip().split()

# Async generator to stream one word at a time
async def generate_stream():
    for word in WORDS:
        yield f"data: {word} \n\n"
        await asyncio.sleep(0.2)  # control the speed of streaming

@app.route('/stream')
async def stream():
    return Response(generate_stream(), content_type='text/event-stream')

if __name__ == '__main__':
    app.run()
