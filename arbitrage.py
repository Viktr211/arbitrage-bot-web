# arbitrage.py
from config import DEFAULT_ASSETS, MAIN_EXCHANGE, AUX_EXCHANGES, MIN_SPREAD_PERCENT, FEE_PERCENT

def find_arbitrage_opportunities(exchanges):
    opportunities = []
    if MAIN_EXCHANGE not in exchanges:
        return opportunities

    main_ex = exchanges[MAIN_EXCHANGE]

    for asset in DEFAULT_ASSETS:
        main_price = get_price(main_ex, asset)
        if not main_price:
            continue

        for aux_name in AUX_EXCHANGES:
            if aux_name in exchanges:
                aux_price = get_price(exchanges[aux_name], asset)
                if aux_price and aux_price < main_price:
                    spread = (main_price - aux_price) / aux_price * 100
                    net_spread = spread - FEE_PERCENT
                    profit = round((main_price - aux_price) * 0.8, 2)  # пример расчёта

                    if net_spread > MIN_SPREAD_PERCENT and profit > 0.3:
                        opportunities.append({
                            'asset': asset,
                            'aux_exchange': aux_name,
                            'main_price': main_price,
                            'aux_price': aux_price,
                            'profit_usdt': profit
                        })
    return sorted(opportunities, key=lambda x: x['profit_usdt'], reverse=True)
