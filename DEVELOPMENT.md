## Test

```
uv run --frozen --group tests pytest
```

## Lint and format

```
uv run --frozen --group dev pre-commit run --all-files
```

## Build docs website

```
uv run --group docs sphinx-build -n -W --keep-going -b html docs docs/_build/html
```