def chunked(items, batch_size):
    if batch_size < 1: raise ValueError("batch_size must be >= 1")
    batch = []
    for item in items:
        batch.append(item)
        if len(batch) == batch_size:
            yield batch
            batch = []
    if batch: yield batch
