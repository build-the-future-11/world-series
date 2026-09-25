"""Resolve historical source identities inside the current extracted repository."""
from pathlib import Path


def source_path(name: str, root: Path = Path('.')) -> Path:
    path = Path(name)
    if path.is_absolute():
        # Older campaign writers saved an absolute path for the study script.
        # Never consult that old checkout, even when it is still available.
        if path.parts[-3:-1] != ('scripts', 'closure'):
            raise ValueError(f'Unsupported historical source path: {name}')
        path = Path('scripts/closure') / path.name
    resolved = (root / path).resolve()
    if not resolved.is_relative_to(root.resolve()):
        raise ValueError(f'Source outside repository: {name}')
    return resolved
