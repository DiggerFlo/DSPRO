"""Answer generation — prompt assembly and LLM call."""


def generate(query: str, context_chunks: list[dict]) -> str:
    """Generate a grounded answer from the query and retrieved context."""
    raise NotImplementedError("Implement generation logic here.")
