from quart import Quart, request, jsonify

app = Quart(__name__)

@app.route('/')
async def home():
    return 'Hello from Quart!'

@app.route('/greet', methods=['GET'])
async def greet():
    name = request.args.get('name', 'World')
    return f'Hello, {name}!'

@app.route('/api/data', methods=['POST'])
async def api_data():
    data = await request.get_json()
    return jsonify({
        "received": data,
        "status": "success"
    })

if __name__ == '__main__':
    app.run()
