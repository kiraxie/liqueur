from .util import LookupDict


_return_codes = {
    0: 'success',
    1000: 'error_login_first',
    1001: 'error_initialize_fail',
    1002: 'error_account_not_exist',
    1003: 'error_account_market_not_match',
    1004: 'error_period_out_of_range',
    1005: 'error_flag_out_of_range',
    1006: 'error_buysell_out_of_range',
    1007: 'error_order_server_invalid',
    1008: 'error_permission_denied',
    1009: 'error_trade_typr_out_of_range',
    1010: 'error_day_trade_out_of_range',
    1011: 'error_order_sign_invalid',
    1012: 'error_new_close_out_of_range',
    1013: 'error_product_invalid',
    1014: 'error_qty_invalid',
    1015: 'error_daytrade_denied',
    1016: 'error_spcial_trade_type_invalid',
    1017: 'error_price_invalid',
    1018: 'error_index_out_of_range',
    1019: 'error_query_in_processing',
    1020: 'error_login_invalid',
    1021: 'error_register_callback',
    1022: 'error_function_permission_denied',
    1023: 'error_market_out_of_range',
    1024: 'error_permission_timeout',
    1025: 'error_foreignstock_price_out_of_range',
    1026: 'error_foreignstock_undefine_cointype',
    1027: 'error_foreignstock_same_coinstype',
    1028: 'error_foreignstock_sale_should_original_coin',
    1029: 'error_foreignstock_trade_unit_invalid',
    1030: 'error_foreignstock_stockno_invalid',
    1031: 'error_foreignstock_accounttype_invalid',
    1032: 'error_foreignstock_initialize_fail',
    1033: 'error_ts_initialize_fail',
    1034: 'error_oversea_trade_product_fail',
    1035: 'error_oversea_trade_data_not_complete',
    1036: 'error_cert_verify_cn_invalid',
    1037: 'error_cert_verify_server_reject',
    1038: 'error_cert_not_verified',
    1039: 'error_oversea_account_not_exist',
    1040: 'error_order_lock',
    1041: 'error_server_not_connected',
    1042: 'error_oversea_kline_data_type_not_found',
    1043: 'error_strikeprice_invalid',
    1044: 'error_callput_invalid',
    1045: 'error_cert_not_found',
    1046: 'error_reserved_out_of_range',
    1047: 'error_smart_trade_order_server_invalid',
    1048: 'error_cancel_order_smartkey_invalid',
    1049: 'error_oversea_future_spread_order',
    1050: 'error_mit_order_exclude_spread_product',
    1051: 'error_sgx_api_order_seqno_confilict',
    1052: 'error_oversea_future_spread_order_no_daytrade',
    1053: 'error_sgx_api_logon_fail',
    1054: 'error_mit_order_must_give_trigger_price',
    1056: 'error_mit_order_must_give_deal_price',
    1057: 'error_withdraw_without_password',
    1058: 'error_withdrawinout_type_out_of_range',
    1059: 'error_currency_out_of_range',
    1060: 'error_ap_gw_server_invalid',
    1061: 'error_strategy_order_buysell_invalid',
    1062: 'error_strategy_order_smartkey_type_invalid',
    1063: 'error_strategy_order_market_type_invalid',
    1064: 'error_strategy_order_trade_type_invalid',
    1065: 'error_correct_price_only_lmt_range',
    1066: 'error_prohibit_emerging_stock_in_continuous_trading',
    1067: 'error_special_trade_type_out_of_range',
    1068: 'error_special_trade_type_is_marketprice_and_orderprice_should_be_zero',
    1069: 'error_market_type_invalid',
    1070: 'error_prohibit_oddlots_afterhours_continuous_trading',
    2001: 'warning_of_com_data_missing',
    2002: 'warning_ts_ready',
    2003: 'warning_login_already',
    2004: 'warning_login_special_already',
    2005: 'warning_cert_verified_already',
    2006: 'warning_order_did_not_locked',
    2007: 'warning_oo_com_quotedata_missing',
    2008: 'warning_oo_com_orderdata_missing',
    2009: 'warning_sign_ts_smarttrade_rick_noitice_first',
    2010: 'warning_sign_ts_smarttrade_rick_noitice_first',
    2011: 'warning_no_function_in_continuous_trading',
    2012: 'warning_osquotecenter_is_not_exist',
    2013: 'warning_initialize_osquotecenter_connection_fail',
    2014: 'warning_initialize_osquotecenter_oo_connection_fail',
    2015: 'warning_download_of_com_data_is_timeout',
    2016: 'warning_download_oo_com_data_is_timeout',
    2017: 'warning_register_replylib_onreplymessage_first',
    3001: 'subject_connection_connected',
    3002: 'subject_connection_disconnect',
    3003: 'subject_connection_stocks_ready',
    3004: 'subject_connection_clear',
    3005: 'subject_connection_reconnect',
    3006: 'subject_quote_page_exceed',
    3007: 'subject_quote_page_incorrect',
    3008: 'subject_tick_page_exceed',
    3009: 'subject_tick_page_incorrect',
    3010: 'subject_tick_stock_not_found',
    3011: 'subject_best5_data_not_found',
    3012: 'subject_quoterequest_not_found',
    3013: 'subject_server_time_not_found',
    3015: 'subject_all_market_ok',
    3016: 'subject_market_info_ready',
    3017: 'subject_catalog_list_ready',
    3018: 'subject_initializestocks',
    3019: 'subject_macd_data_not_found',
    3020: 'subject_booltunel_data_not_found',
    3021: 'subject_connection_fail',
    3022: 'subject_connection_solclientapi_fail',
    3023: 'subject_stockno_is_invalid',
    3024: 'subject_market_no_is_out_of_range',
    3025: 'subject_cant_accept_spread_stockno',
    3026: 'subject_connection_sgx_api_ready',
    151: 'error_login_wrong_password',
    152: 'error_login_wrong_password_over_limit',
    153: 'error_login_wrong_id',
    4001: 'kline_data_type_not_found',
    151: 'error_login_wrong_password',
    152: 'error_login_wrong_password_over_limit',
    153: 'error_login_wrong_id',
    9999: 'fail'
}

_market_no = {
    0: 'listed_at_exchange',
    1: 'listed_at_over_the_counter',
    2: 'feature',
    3: 'option',
    4: 'listed_at_emerging'
}

_kbar_type = {
    0: 'one_min',
    4: 'day',
    5: 'week',
    6: 'month'
}

_kbar_out_type = {
    0: 'old',
    1: 'new'
}

_kbar_trade_session = {
    0: 'all_day',
    1: 'daylight',
}

return_codes = LookupDict(name='return_codes')

market_no = LookupDict(name='market_number')

kbar_type = LookupDict(name='kbar_type_number')

kbar_out_type = LookupDict(name='kbar_out_format_type')

kbar_trade_session = LookupDict(name='kbar_trade_session_type')


def _init():
    for k, v in _return_codes.items():
        setattr(return_codes, v, k)

    for k, v in _market_no.items():
        setattr(market_no, v, k)

    for k, v in _kbar_type.items():
        setattr(kbar_type, v, k)

    for k, v in _kbar_out_type.items():
        setattr(kbar_out_type, v, k)

    for k, v in _kbar_trade_session.items():
        setattr(kbar_trade_session, v, k)


_init()
