# apiaberta-py

Official Python SDK for [API Aberta](https://apiaberta.pt) — the unified REST API for Portuguese public data.

[![PyPI version](https://img.shields.io/pypi/v/apiaberta)](https://pypi.org/project/apiaberta/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://python.org)

## Install

```bash
pip install apiaberta
```

> Requires Python 3.8+ and `requests`.

## Quick Start

```python
from apiaberta import ApiAberta

api = ApiAberta(api_key="your-key-here")

# Fuel prices in Lisboa
prices = api.fuel(district="Lisboa")
print(prices["data"])

# Weather forecast for all cities
weather = api.weather(days=3)
print(weather["data"][0])

# Active civil protection incidents
incidents = api.active_incidents()
print(f"{incidents['count']} active incidents")
```

## API Reference

### `ApiAberta(api_key=None, base_url=..., timeout=10)`

| Parameter  | Type    | Default                       | Description                      |
|------------|---------|-------------------------------|----------------------------------|
| `api_key`  | `str`   | `APIABERTA_KEY` env var       | API key from apiaberta.pt        |
| `base_url` | `str`   | `https://api.apiaberta.pt/v1` | Override the API base URL        |
| `timeout`  | `float` | `10.0`                        | Request timeout in seconds       |

### Methods

#### Combustíveis

```python
# All prices (optionally filtered)
api.fuel(district="Porto", fuel="diesel")

# Gas stations
api.fuel_stations(district="Lisboa", limit=50)
```

#### Meteorologia (IPMA)

```python
# Forecast for all cities
api.weather(days=5)

# Forecast for a specific city (Lisboa = 1110600)
api.weather_city(1110600)

# Active meteorological warnings
api.weather_warnings(level="orange")
```

#### Proteção Civil (ANPC)

```python
# Active incidents (default)
api.incidents(district="Faro", limit=10)

# Active incidents shortcut
api.active_incidents()

# Historical incidents
api.incidents(active=False, from_date="2025-08-01", to_date="2025-08-31")
```

#### Estatísticas (INE/Eurostat)

```python
# All indicators
api.stats()

# Specific indicator
api.stats(indicator="population")
api.stats(indicator="gdp")
api.stats(indicator="unemployment")
```

#### Veículos Elétricos

```python
api.ev()
```

#### Contratos Públicos (BASE)

```python
api.contracts(query="consultoria", from_date="2024-01-01", limit=20)
```

#### Plataforma

```python
# Platform status
api.status()

# Your API usage (requires api_key)
api.usage()
```

### Error Handling

```python
from apiaberta import ApiAberta, ApiAbertaError

api = ApiAberta(api_key="your-key")

try:
    data = api.fuel()
except ApiAbertaError as e:
    print(f"API error {e.status_code}: {e}")
```

## Environment Variables

| Variable        | Description                                        |
|-----------------|----------------------------------------------------|
| `APIABERTA_KEY` | Your API key (alternative to passing it in options)|

## Get an API Key

Register for free at [apiaberta.pt](https://apiaberta.pt) to get your API key.

## License

MIT — see [LICENSE](LICENSE)
