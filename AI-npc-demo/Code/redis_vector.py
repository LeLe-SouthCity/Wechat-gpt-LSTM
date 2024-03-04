from langchain_agent.imports import *
os.environ["OPENAI_API_KEY"] = "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"#getpass.getpass("OpenAI API Key:")


from langchain_openai import OpenAIEmbeddings

embeddings = OpenAIEmbeddings()

metadata = [
    {
        "user": "john",
        "age": 18,
        "job": "engineer",
        "credit_score": "high",
    },
    {
        "user": "derrick",
        "age": 45,
        "job": "doctor",
        "credit_score": "low",
    },
    {
        "user": "nancy",
        "age": 94,
        "job": "doctor",
        "credit_score": "high",
    },
    {
        "user": "tyler",
        "age": 100,
        "job": "engineer",
        "credit_score": "high",
    },
    {
        "user": "joe",
        "age": 35,
        "job": "dentist",
        "credit_score": "medium",
    },
]
texts = ["foo", "foo", "foo", "bar", "bar"]


rds = Redis.from_texts(
    texts,
    embeddings,
    metadatas=metadata,
    redis_url="redis://localhost:6379",
    index_name="users",
)

rds.index_name
