from dataclasses import asdict, dataclass


@dataclass
class Paper:
    """Unified Domain Model for research papers across all fetchers."""
    id: str
    title: str
    published: str
    summary: str
    link: str
    category: str
    source: str

    def to_dict(self) -> dict:
        """Convert the dataclass instance to a dictionary for JSON serialization."""
        return asdict(self)