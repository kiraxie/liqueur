from liqueur import Liqueur, Config, kbar_type, market_no
from datetime import datetime


conf = Config('.')
conf.from_mapping({
    'account': {
        'username': 'A123456789',
        'password': 'xxxxxxxx'
    },
    'subscription': {
        'quote': [2330],
        'detail': [2330],
        'kbar': [(2330, kbar_type.day)],
        'tick': [],
        'stocks_of_market': [market_no.listed_at_exchange]
    }
})

app = Liqueur(conf)


@app.hook_message()
def message_handler(message):
    print(message, end='')


@app.hook_time()
def time_handler(t):
    print(t)


@app.hook_quote()
def q_handler(q):
    print(q)


@app.hook_tick()
def t_handler(t):
    print(t)


@app.hook_kbar()
def kbar_handler(k):
    print(k)


@app.hook_best_five()
def bf_handler(bf):
    print(bf)


if __name__ == "__main__":
    app.run()
