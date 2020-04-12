# Liqueur

Liqueur is a lightweight trade framework for Taiwan stock market based on Taiwan securities broker company [Capital](https://www.capital.com.tw/)'s API. It is designed to make application start quickly and easy to use, so user can focus on strategy development.

## Requirement

[Capital API v2.13.20](https://www.capital.com.tw/Service2/download/api_zip/CapitalAPI_2.13.20.zip)

## Installation

Install the framework with pip:

```bash
pip install Liqueur
```

## Quick Start

```python
from liqueur import Liqueur, Config

conf = Config('.')
conf.from_mapping({
    "account": {
        "username": "A123456789",
        "password": "xxxxxxxx"
    },
    "subscription": {
        "quote": [2330],
        "detail": [],
        "kbar": [],
        "tick": []
    }
})

app = Liqueur(conf)


@app.hook_message()
def message_handler(message):
    print(message, end='')

@app.hook_quote()
def quote_handler(quote):
    print(quote)

if __name__ == "__main__":
    app.run()
```

```bash
$ python myapp.py
Login......ok
Connect......success
{
    "datetime": "2019-09-10 14:00:00.847484",
    "timestamp": 1568132147.847484,
    "orderbook_id": "2330",
    "name": "台積電",
    "high_price": 264.0,
    "open_price": 263.5,
    "low_price": 260.5,
    "close_price": 261.5,
    "bid_price": 261.5,
    "bid_qty": 251,
    "ask_price": 262.0,
    "ask_qty": 580,
    "buy_qty": 10733,
    "sell_qty": 18537,
    "tick_qty": 10,
    "total_qty": 29270,
    "ref_qty": 17186,
    "ref_price": 265.0,
    "up_price": 291.5,
    "down_price": 238.5,
    "simulate": 0
}
```
