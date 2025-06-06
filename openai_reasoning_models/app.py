from openai import OpenAI

client = OpenAI(api_key="")

response = client.responses.create(
    model="o4-mini",
    input="compare gdp of thailand and vietnam",
    reasoning={"effort": "medium", "summary": "auto"}
)

print(response.model_dump_json(indent=2))