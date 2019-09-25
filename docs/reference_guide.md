# Liqueur Reference Guide

## Table of Contents

* [Application](#application)
  * [Liqueur](#liqueur)
* [Data Type](#data-type)
  * [QuoteData](#quotedata)
  * [Tick](#tick)
  * [KBar](#k-bar)
  * [Price Quantity](#price-quantity)
  * [Best Five Price](#best-five-price)
* [Codes](#codes)
  * [Return Code](#return-code)
  * [Market Number](#market-number)
  * [K Bar Type](#k-bar-type)
  * [K Bar Trade Session](#k-bar-trade-session)

## Application

### Liqueur

#### Constructure {#liqueur_construct}

```py
def __init__(self, conf):
```

|Variable Name|Type|
|---|---|
|conf|```dict```|
|*return*|```Liqueur```|

### Public Member Functions {#liqueur_public_fn}

```py
def run(self)
```

Runs the application.

The function follows the steps as below:

  1. Hook the application signal event.
  2. Hook the API event to API module.
  3. Sign in to Capital server.
  4. Waitting the application until terminating.
  5. Exit the quote receiving mode when application terminates.

|Variable Name|Type|
|---|---|
|None||

```py
def terminate(self):
```

Terminate the application.

|Variable Name|Type|
|---|---|
|None||

```py
def hook_time(self, rule=0):
```

Decorator which hooks the time callback function.
These functions will be excuted when time event was triggered.

By default, the heartbeat was hooked on this delegation group in class initialization.

|Variable Name|Type|
|---|---|
|rule|```int```|

```py
def append_time_delegate(self, rule=0):
```

Function way to hook the time callback function.

|Variable Name|Type|
|---|---|
|rule|```int```|

```py
def hook_message(self, rule=0):
```

Decorator which hooks the message callback function.

By default, the application DOES NOT print or log any message, so the developer can choose what it does when message pops out.

|Variable Name|Type|
|---|---|
|rule|```int```|

```py
def append_message_delegate(self, rule=0):
```

Function way to hook the message callback function.

|Variable Name|Type|
|---|---|
|rule|```int```|

```py
def hook_quote(self, rule=0):
```

Decorator which hooks the quote callback function.

|Variable Name|Type|
|---|---|
|rule|```int```|

```py
def append_quote_delegate(self, rule=0):
```

Function way to hook the quote callback function.

|Variable Name|Type|
|---|---|
|rule|```int```|

```py
def hook_kbar(self, rule=0):
```

Decorator which hooks the K bar callback function.

|Variable Name|Type|
|---|---|
|rule|```int```|

```py
def append_kbar_delegate(self, rule=0):
```

Function way to hook the K bar callback function.

|Variable Name|Type|
|---|---|
|rule|```int```|

```py
def hook_best_five(self, rule=0):
```

Decorator which hooks the best five prices callback function.

|Variable Name|Type|
|---|---|
|rule|```int```|

```py
def append_best_five_delegate(self, rule=0):
```

Function way to hook the best five prices callback function.

|Variable Name|Type|
|---|---|
|rule|```int```|

```py
def hook_stocks_of_market(self, rule=0):
```

Decorator which hooks the stock of market callback function.

|Variable Name|Type|
|---|---|
|rule|```int```|

```py
def append_stocks_of_market_delegate(self, rule=0):
```

Function way to hook the stock of market callback function.

|Variable Name|Type|
|---|---|
|rule|```int```|

```py
def message(self, message_str):
```

External message interface.

|Variable Name|Type|
|---|---|
|message_str|```string```|

#### Properties {#liqueur_properties}

|Property Name|Type|Decription|
|---|---|---|
|config|```Config```|The configuration of application|

## Data Type

### QuoteData

#### Constructure {#quote_construct}

```py
def __init__(self, dt, *args, **kwargs)
```

Recommand using ```from_quote``` or ```from_dict``` functions instead of construct.

|Variable Name|Type|
|---|---|
|dt|```datetime```|
|*args|```list```|
|**kwargs|```dict```|
|*return*|```QuoteData```|

#### Public Member Functions {#quote_public_fn}

```py
def to_dict(self)
```

Format the ```QuoteData``` data to ```dict```.

|Variable Name|Type|
|---|---|
|None||
|*return*|```dict```|

#### Class Member Functions {#quote_class_fn}

```py
def from_dict(cls, dict_data)
```

New a ```QuoteData``` from a dict variable.

|Variable Name|Type|
|---|---|
|dict_data|```dict```|
|*return*|```QuoteData```|

```py
def from_quote(cls, orderbook_id, name, high_price, open_price, low_price, close_price,
               bid_price, bid_qty, ask_price, ask_qty, buy_qty, sell_qty, tick_qty, total_qty,
               ref_qty, ref_price, up_price, down_price, simulate)
```

New a ```QuoteData``` from variables.

|Variable Name|Type|
|---|---|
|orderbook_id|```string```|
|name|```string```|
|high_price|```float```|
|open_price|```float```|
|low_price|```float```|
|close_price|```float```|
|bid_price|```float```|
|bid_qty|```int```|
|ask_price|```float```|
|ask_qty|```int```|
|buy_qty|```float```|
|sell_qty|```int```|
|tick_qty|```int```|
|total_qty|```int```|
|ref_price|```float```|
|ref_qty|```int```|
|up_price|```float```|
|down_price|```float```|
|simulate|```bool```|
|*return*|```QuoteData```|

#### Properties {#quote_properties}

|Property Name|Type|Decription|
|---|---|---|
|datetime|```datetime```|The date and time as ```datetime``` format|
|timestamp|```int```|The property ```datetime``` as a POSIX timestamp|
|orderbook_id|```string```|The stock code in Taiwan exchange|
|name|```string```|The stock name in chinese|
|high_price|```float```|Highest trade price for the current day|
|open_price|```float```|The opening price is set to the price of the first trade|
|low_price|```float```|Lowest trade price for the current day|
|close_price|```float```|The closing price is set to the price of the last trade|
|bid_price|```float```|Best bid price at first element|
|bid_qty|```int```|Quantity for bid price levels|
|ask_price|```float```|Best ask price at first element|
|ask_qty|```int```|Quantity for ask price levels|
|buy_qty|```float```|Total quantity for bid price|
|sell_qty|```int```|Total quantity for ask price|
|tick_qty|```int```|Current traded quantity|
|total_qty|```int```|Total traded quantity today|
|ref_price|```float```|The close price of previous trading day|
|ref_qty|```int```|The total quantity of previous trading day|
|up_price|```float```|Limit up price|
|down_price|```float```|Limit down price|
|simulate|```bool```|Simulate trade flag|

### Tick

#### Constructure {#tick_construct}

```py
def __init__(self, dt, orderbook_id, name, bid, ask, close, qty, simulate)
```

Recommand using ```from_tick``` or ```from_dict``` functions instead of construct.

|Variable Name|Type|
|---|---|
|dt|```datetime```|
|orderbook_id|```string```|
|name|```string```|
|bid|```float```|
|ask|```float```|
|close|```float```|
|qty|```int```|
|*return*|```Tick```|

#### Public Member Functions {#tick_public_fn}

```py
def to_dict(self)
```

Format the ```Tick``` information to ```dict```.

|Variable Name|Type|
|---|---|
|None||
|*return*|```dict```|

#### Class Member Functions {#tick_class_fn}

```py
def from_dict(cls, dict_data)
```

New a ```Tick``` from a dict variable.

|Variable Name|Type|
|---|---|
|dict_data|```dict```|
|*return*|```Tick```|

```py
def from_tick(cls, dt, orderbook_id, name, bid, ask, close, qty, simulate)
```

New a ```Tick``` from variables.

|Variable Name|Type|
|---|---|
|dt|```datetime```|
|orderbook_id|```string```|
|name|```string```|
|bid|```float```|
|ask|```float```|
|close|```float```|
|qty|```int```|
|simulate|```bool```|
|*return*|```Tick```|

#### Properties {#tick_properties}

|Property Name|Type|Decription|
|---|---|---|
|datetime|```datetime```|The date and time as ```datetime``` format|
|timestamp|```int```|The property ```datetime``` as a POSIX timestamp|
|orderbook_id|```string```|The stock code in Taiwan exchange|
|name|```string```|The stock name in chinese|
|bid_price|```float```|Best bid price of this tick|
|ask_price|```float```|Best ask price of this tick|
|close_price|```float```|The close price of this tick|
|qty|```float```|The traded quantity of this tick|
|simulate|```bool```|Simulate trade flag|

### K Bar

#### Constructure {#kbar_construct}

```py
def __init__(self, orderbook_id, dt, open_price, high_price, low_price, close_price, qty)
```

Recommand using ```from_kbar```, ```from_kbar_string``` or ```from_dict``` functions instead of construct.

|Variable Name|Type|
|---|---|
|orderbook_id|```string```|
|dt|```datetime```|
|open_price|```float```|
|high_price|```float```|
|low_price|```float```|
|close_price|```float```|
|qty|```int```|
|*return*|```Kbar```|

#### Public Member Functions {#kbar_public_fn}

```py
def to_dict(self)
```

Format the ```Kbar``` information to ```dict```.

|Variable Name|Type|
|---|---|
|None||
|*return*|```dict```|

#### Class Member Functions {#kbar_class_fn}

```py
def from_dict(cls, dict_data)
```

New a ```Kbar``` from a dict variable.

|Variable Name|Type|
|---|---|
|dict_data|```dict```|
|*return*|```Kbar```|

```py
def from_kbar(cls, orderbook_id, time_string, open_price, high_price, low_price, close_price, qty)
```

New a ```Kbar``` from variables.

|Variable Name|Type|
|---|---|
|orderbook_id|```string```|
|time_string|```string```|
|open_price|```float```|
|high_price|```float```|
|low_price|```float```|
|close_price|```float```|
|qty|```int```|
|*return*|```Kbar```|

```py
def from_kbar_string(cls, orderbook_id, string_data)
```

New a ```Kbar``` from Capital API K line callback function string.

|Variable Name|Type|
|---|---|
|orderbook_id|```string```|
|string_data|```string```|
|*return*|```Kbar```|

```py
def red_kbar(cls)
```

Return the type of red K bar value.

|Variable Name|Type|
|---|---|
|None||
|*return*|```1```|

```py
def cross_kbar(cls)
```

Return the type of cross K bar value.

|Variable Name|Type|
|---|---|
|None||
|*return*|```0```|

```py
def black_kbar(cls)
```

Return the type of black K bar value.

|Variable Name|Type|
|---|---|
|None||
|*return*|```-1```|

#### Properties {#kbar_properties}

|Property Name|Type|Decription|
|---|---|---|
|datetime|```datetime```|The date and time as ```datetime``` format|
|timestamp|```int```|The property ```datetime``` as a POSIX timestamp|
|orderbook_id|```string```|The stock code in Taiwan exchange|
|open_price|```float```|The open price of this K bar|
|high_price|```float```|Highest price of this K bar|
|low_price|```float```|Lowest price of this K bar|
|close_price|```float```|The close price of this K bar|
|qty|```int```|The traded quantity of this tick|
|bar|```float```|The K bar body|
|up_shadow|```float```|The length of up shadow line|
|down_shadow|```float```|The length of down shadow line|
|head|```float```|The high price of K bar body|
|foot|```float```|The low of K bar body|
|pattern|```int```|The K bar type|

### PriceQty

#### Constructure {#pxqty_construct}

```py
def __init__(self, price=-1, qty=-1)
```

The element of best five price.

|Variable Name|Type|
|---|---|
|price|```float```|
|qty|```int```|
|*return*|```PriceQty```|

#### Public Member Functions {#pxqty_public_fn}

```py
def to_dict(self)
```

Format the ```PriceQty``` information to ```dict```.

|Variable Name|Type|
|---|---|
|None||
|*return*|```dict```|

#### Class Member Functions {#pxqty_class_fn}

```py
def from_dict(cls, dict_data)
```

New a ```PriceQty``` from a dict variable.

|Variable Name|Type|
|---|---|
|dict_data|```dict```|
|*return*|```PriceQty```|

#### Properties {#pxqty_properties}

|Property Name|Type|Decription|
|---|---|---|
|price|```datetime```|The price of this element|
|qty|```int```|The quantity of this element|

### BestFivePrice

#### Constructure {#best5_construct}

```py
def __init__(self, orderbook_id, dt, bid_py, ask_py)
```

Recommand using ```from_best_five``` or ```from_dict``` functions instead of construct.

|Variable Name|Type|
|---|---|
|orderbook_id|```string```|
|dt|```datetime```|
|bid_py|```List``` of ```PriceQty```|
|ask_py|```List``` of ```PriceQty```|
|*return*|```BestFivePrice```|

#### Public Member Functions {#best5_public_fn}

```py
def to_dict(self)
```

Format the ```BestFivePrice``` information to ```dict```.

|Variable Name|Type|
|---|---|
|None||
|*return*|```dict```|

#### Class Member Functions {#best5_class_fn}

```py
def from_dict(cls, dict_data)
```

New a ```BestFivePrice``` from a dict variable.

|Variable Name|Type|
|---|---|
|dict_data|```dict```|
|*return*|```BestFivePrice```|

```py
def from_best_five(cls, orderbook_id, bid_py, ask_py)
```

New a ```BestFivePrice``` from variables.

|Variable Name|Type|
|---|---|
|orderbook_id|```string```|
|bid_py|```List``` of ```PriceQty```|
|ask_py|```List``` of ```PriceQty```|
|*return*|```BestFivePrice```|

#### Properties {#best5_properties}

|Property Name|Type|Decription|
|---|---|---|
|datetime|```datetime```|The date and time as ```datetime``` format|
|timestamp|```int```|The property ```datetime``` as a POSIX timestamp|
|orderbook_id|```string```|The stock code in Taiwan exchange|
|bid_py|```list```|The best five bid PriceQty elements|
|ask_py|```list```|The best five ask PriceQty elements|

## Codes

### Return Code

Detail meaning in offical document chapter 6.

|Variable Name|Value|
|---|---|
|success|0|
|error_login_first|1000|
|error_initialize_fail|1001|
|error_account_not_exist|1002|
|error_account_market_not_match|1003|
|error_period_out_of_range|1004|
|error_flag_out_of_range|1005|
|error_buysell_out_of_range|1006|
|error_order_server_invalid|1007|
|error_permission_denied|1008|
|error_trade_typr_out_of_range|1009|
|error_day_trade_out_of_range|1010|
|error_order_sign_invalid|1011|
|error_new_close_out_of_range|1012|
|error_product_invalid|1013|
|error_qty_invalid|1014|
|error_daytrade_denied|1015|
|error_spcial_trade_type_invalid|1016|
|error_price_invalid|1017|
|error_index_out_of_range|1018|
|error_query_in_processing|1019|
|error_login_invalid|1020|
|error_register_callback|1021|
|error_function_permission_denied|1022|
|error_market_out_of_range|1023|
|error_permission_timeout|1024|
|error_foreignstock_price_out_of_range|1025|
|error_foreignstock_undefine_cointype|1026|
|error_foreignstock_same_coinstype|1027|
|error_foreignstock_sale_should_original_coin|1028|
|error_foreignstock_trade_unit_invalid|1029|
|error_foreignstock_stockno_invalid|1030|
|error_foreignstock_accounttype_invalid|1031|
|error_foreignstock_initialize_fail|1032|
|error_ts_initialize_fail|1033|
|error_oversea_trade_product_fail|1034|
|error_oversea_trade_data_not_complete|1035|
|error_cert_verify_cn_invalid|1036|
|error_cert_verify_server_reject|1037|
|error_cert_not_verified|1038|
|error_oversea_account_not_exist|1039|
|error_order_lock|1040|
|error_server_not_connected|1041|
|error_oversea_kline_data_type_not_found|1042|
|error_strikeprice_invalid|1043|
|error_callput_invalid|1044|
|error_cert_not_found|1045|
|error_reserved_out_of_range|1046|
|error_smart_trade_order_server_invalid|1047|
|error_cancel_order_smartkey_invalid|1048|
|error_oversea_future_spread_order|1049|
|error_mit_order_exclude_spread_product|1050|
|error_sgx_api_order_seqno_confilict|1051|
|error_oversea_future_spread_order_no_daytrade|1052|
|error_sgx_api_logon_fail|1053|
|error_mit_order_must_give_trigger_price|1054|
|error_mit_order_must_give_deal_price|1056|
|error_withdraw_without_password|1057|
|error_withdrawinout_type_out_of_range|1058|
|error_currency_out_of_range|1059|
|error_ap_gw_server_invalid|1060|
|error_strategy_order_buysell_invalid|1061|
|error_strategy_order_smartkey_type_invalid|1062|
|error_strategy_order_market_type_invalid|1063|
|error_strategy_order_trade_type_invalid|1064|
|error_correct_price_only_lmt_range|1065|
|1066|1066|
|error_special_trade_type_out_of_range|1067|
|1068|1068|
|error_market_type_invalid|1069|
|1070|1070|
|warning_of_com_data_missing|2001|
|warning_ts_ready|2002|
|warning_login_already|2003|
|warning_login_special_already|2004|
|warning_cert_verified_already|2005|
|warning_order_did_not_locked|2006|
|warning_oo_com_quotedata_missing|2007|
|warning_oo_com_orderdata_missing|2008|
|warning_sign_ts_smarttrade_rick_noitice_first|2009|
|warning_sign_ts_smarttrade_rick_noitice_first|2010|
|warning_no_function_in_continuous_trading|2011|
|warning_osquotecenter_is_not_exist|2012|
|2013|2013|
|2014|2014|
|warning_download_of_com_data_is_timeout|2015|
|warning_download_oo_com_data_is_timeout|2016|
|warning_register_replylib_onreplymessage_first|2017|
|subject_connection_connected|3001|
|subject_connection_disconnect|3002|
|subject_connection_stocks_ready|3003|
|subject_connection_clear|3004|
|subject_connection_reconnect|3005|
|subject_quote_page_exceed|3006|
|subject_quote_page_incorrect|3007|
|subject_tick_page_exceed|3008|
|subject_tick_page_incorrect|3009|
|subject_tick_stock_not_found|3010|
|subject_best5_data_not_found|3011|
|subject_quoterequest_not_found|3012|
|subject_server_time_not_found|3013|
|subject_all_market_ok|3015|
|subject_market_info_ready|3016|
|subject_catalog_list_ready|3017|
|subject_initializestocks|3018|
|subject_macd_data_not_found|3019|
|subject_booltunel_data_not_found|3020|
|subject_connection_fail|3021|
|subject_connection_solclientapi_fail|3022|
|subject_stockno_is_invalid|3023|
|subject_market_no_is_out_of_range|3024|
|subject_cant_accept_spread_stockno|3025|
|subject_connection_sgx_api_ready|3026|
|error_login_wrong_password|151|
|error_login_wrong_password_over_limit|152|
|error_login_wrong_id|153|
|kline_data_type_not_found|4001|
|error_login_wrong_password|151|
|error_login_wrong_password_over_limit|152|
|error_login_wrong_id|153|
|fail|9999|

### Market Number

|Variable Name|Value|
|---|---|
|listed_at_exchange|0|
|listed_at_over_the_counter|1|
|feature|2|
|option|3|
|listed_at_emerging|4|

### K Bar Type

|Variable Name|Value|
|---|---|
|listed_at_exchange|0|
|listed_at_over_the_counter|1|
|feature|2|
|option|3|
|listed_at_emerging|4|

### K Bar Trade Session

|Variable Name|Value|
|---|---|
|one_min|0|
|day|4|
|week|5|
|month|6|
