import asyncio, hashlib
from .batching import chunked
from .cache import TTLCache

def mock_inference(text):
    """Demonstration placeholder; replace with a real validated model call."""
    terms = ["Python", "SQL", "Excel", "Power BI", "machine learning", "pandas"]
    lower = text.lower()
    return {"word_count": len(text.split()), "skills": [s for s in terms if s.lower() in lower], "mock": True}

async def process_one(text, cache, delay_seconds):
    key = "mock-v1:" + hashlib.sha256(text.encode("utf-8")).hexdigest()
    cached = cache.get(key)
    if cached is not None: return {"result": cached, "cache_hit": True}
    await asyncio.sleep(delay_seconds)  # simulated I/O, not real inference
    result = mock_inference(text); cache.set(key, result)
    return {"result": result, "cache_hit": False}

async def process_resumes(texts, batch_size=8, max_concurrency=4, delay_seconds=0.002, cache=None):
    if max_concurrency < 1: raise ValueError("max_concurrency must be >= 1")
    cache = cache or TTLCache()
    semaphore = asyncio.Semaphore(max_concurrency)
    output = []
    async def limited(text):
        async with semaphore: return await process_one(text, cache, delay_seconds)
    for batch in chunked(texts, batch_size):
        output.extend(await asyncio.gather(*(limited(t) for t in batch)))
    return {"processed": len(output), "results": output,
            "cache_hits": sum(x["cache_hit"] for x in output),
            "cache_hit_rate": cache.hit_rate, "cache_size": cache.size}
