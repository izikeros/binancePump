# binancePump

Binance Pump Detector 


## How it works?
Creates a binance web socket and listen for trades. Aggregates information, groups trade information via price, ticks and volume.
prints out at the time interval most traded, price changed and volume changed symbol.
This information could be detected an anomaly. An anomaly in binance could be leading to pump or dump.

## How to run

```bash
$ git clone https://github.com/ogu83/binancePump.git
$ pip3 install termcolor joblib tqdm numpy pandas python-binance pyTelegramBotAPI
```
Requires api details for telegram bot and for binance client. Before running, create own `api_config.json` and fill with keys and secret (remember not  to put these secrets into public repository).

Finally, run the detector:
```bash
$ python3 binancePump.py
```

## Screen Shot

![Screenshot](binancePumpterminal.png)

## Credits
This project is a fork of [ogu83/binancePump](https://github.com/ogu83/binancePump). Credits to original author: [ogu83](https://github.com/ogu83).

## See also:
https://python-binance.readthedocs.io/en/latest/websockets.html
