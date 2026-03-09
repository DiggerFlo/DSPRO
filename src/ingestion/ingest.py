"""Data ingestion pipeline — loads raw articles into data/raw/."""


def ingest() -> None:
    """Ingest articles from the configured source."""
    raise NotImplementedError("Implement ingestion logic here.")


if __name__ == "__main__":
    ingest()
