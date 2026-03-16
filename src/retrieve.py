"""Retrieval — semantic search over the embedded corpus."""


def retrieve(query: str, top_k: int = 5) -> list[dict]:
    """Return the top-k most relevant chunks for a given query."""
    raise NotImplementedError("Implement retrieval logic here.")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--query", required=True)
    args = parser.parse_args()
    results = retrieve(args.query)
    for r in results:
        print(r)
