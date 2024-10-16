import asyncio
from playwright.async_api import async_playwright, expect, Page
from wallet_settings import seed, SOLFLARE_EXTENSION_PATH, MM_PASSWORD                            # файл с паролем, сид фразой и путь до манифеста
from playwright.sync_api import BrowserContext
from functions import (swap, open_position, close_position, connect_wallet, get_balance_token, find_page,
                       wallet_functions, authorization, sell_position, range_price)               # файл с функциями
from constants import (token_address, transaction_button, meteora_btn_con, page_url, jup_swap_url, jup_btn_con,
                       connect_button, DEFAULT_DELAY)                                             # файл с переменными


async def main():
    while True:
        async with async_playwright() as p:
            context = await p.chromium.launch_persistent_context(
                '',
                headless=False,
                slow_mo=1600,
                args=[
                    f'--disable-extensions-except={SOLFLARE_EXTENSION_PATH}',
                    f'--load-extension={SOLFLARE_EXTENSION_PATH}',
                    '--disable-blink-features=AutomationControlled',
                ],
            )

            titles = [await p.title() for p in context.pages]
            while 'Solflare' not in titles:
                titles = [await p.title() for p in context.pages]

            # Логинимся в кошельке
            await authorization(context=context, seed=seed, password=MM_PASSWORD)

            #   Идём на юпитер и коннектим кошелёк
            jup_page = context.pages[0]
            await connect_wallet(url=jup_swap_url, button=jup_btn_con, page=jup_page)
            await wallet_functions(context=context, button=connect_button)

            # Проверяем баланс USDT
            balance_from_token, balance_to_token = await get_balance_token(stable_coin='jlp', need_coin='usdt', page=jup_page)

            # Если jlp больше 20, а usdt < 3, то меняем jlp на usdt:
            if balance_to_token < 3 and balance_from_token > 20:
                quantity_swap = '3'
                await swap(page=jup_page, quantity=quantity_swap)
                await wallet_functions(context=context, button=transaction_button)

            # Проверяем баланс sol
            balance_from_token, balance_to_token = await get_balance_token(stable_coin='usdt', need_coin='sol', page=jup_page)

            # Если sol меньше 0.08 и usdt > 2, то докупаем sol на 3$
            if balance_to_token < 0.08 and balance_from_token > 2:
                quantity_swap = '3'
                await swap(page=jup_page, quantity=quantity_swap)
                await wallet_functions(context=context, button=transaction_button)

            # Проверяем баланс jlp
            balance_from_token, balance_to_token = await get_balance_token(stable_coin='usdt', need_coin='jlp', page=jup_page)

            # Если jlp меньше 5 и usdt > 2, то докупаем jlp на 2$
            if balance_to_token < 5 and balance_from_token > 2:
                print('Меняем USDT=', balance_from_token-3)
                quantity_swap = (balance_from_token-3)
                quantity_swap = round(quantity_swap, 2)
                quantity_swap = str(quantity_swap)
                quantity_swap = quantity_swap.replace('.',',')
                await swap(page=jup_page, quantity=quantity_swap)
                await wallet_functions(context=context, button=transaction_button)


            # Идём на метеору и подключаем кошелёк
            page = await context.new_page()
            await page.wait_for_load_state()
            await connect_wallet(url=page_url, button=meteora_btn_con, page=page)

            # Ждем всплывающее окно Solflare и подтверждаем подключение
            await wallet_functions(context=context, button=connect_button)

            # ТЕСТОВАЯ работа с сайтом, поиск пула
            inputs = page.locator('//*[@id="__next"]/div[1]/div[5]/div/div[2]/div[2]/div/div[1]/div/div/input')
            await expect(inputs.first).to_be_visible(timeout=20000)
            await inputs.first.type('jlp', delay=DEFAULT_DELAY)

            try:
                pool = page.get_by_text('JLP-USDT', exact=True)
                await expect(pool.first).to_be_visible()
                await pool.first.scroll_into_view_if_needed()
                await pool.first.click()

            except Exception as e:
                print(f'Искомой пары нет: {e}')
                await context.close()

            await page.locator('//*[@id="__next"]/div[1]/div[5]/div/div[2]/div[2]/div/div[4]/div/div[1]/div/div/div['
                                    '3]/div[2]/div/a[1]').click()                          # Первый пул

            try:
                await close_position(page=page)
                await wallet_functions(context=context, button=transaction_button)
                print('Была открытая позиция')

            except:
                print('Нет открытых позиций')

            # Открываем позицию
            await open_position(page=page)
            await wallet_functions(context=context, button=transaction_button)
            head_range_price, low_range_price = await range_price(page=page)
            print('Верхняя границе рейнджа=', head_range_price)
            print('Нижняя границе рейнджа=', low_range_price)
            sell_price = low_range_price + (head_range_price - low_range_price) * 0.95
            print('Цена продажи=', sell_price)
            await sell_position(page=page, sell_price=sell_price)
            # Закрываем позицию
            await close_position(page=page)
            await wallet_functions(context=context, button=transaction_button)
            print('Позиция закрыта в связи с достижением указанной цены')
            await asyncio.sleep(30)
            await context.close()


if __name__ == '__main__':
    asyncio.run(main())
