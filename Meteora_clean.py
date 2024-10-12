import asyncio
from playwright.async_api import async_playwright, expect, Page
from playwright.sync_api import BrowserContext, Browser
import wallet_settings as psw   # файл с паролем, сид фразой и путь до манифеста

meteora_btn_con = '//button[contains(@class, "bg-[#191C32]")]'
jup_btn_con = '//*[@id="__next"]/div[2]/div[1]/div/div[4]/div[3]/div/button[2]/div/span[2]'
DEFAULT_DELAY = 300
page_url = 'https://app.meteora.ag/'
jup_swap_url = 'https://jup.ag/'
token_address = {'USDT' : 'Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB',
                 'SOL' : 'So11111111111111111111111111111111111111112',
                 'JLP' : '27G8MtK7VtTcCHkpASjSDdkWWYfoqT6ggEuKidVJidD4'}
connect_button = '//html/body/div[2]/div[2]/div/div[3]/div/button[2]'
transaction_button = '//html/body/div[2]/div[2]/div/div[2]/div/div[2]/div[2]/div[2]/button[2]'

# Функция свапа
async def swap(page: Page):
    await page.locator('//*[@id="__next"]/div[2]/div[3]/div[2]/div[2]/div[2]/div[2]/form/div[1]/div['
                       '1]/div[2]/span/div/input').fill('2')
    but_swp = page.locator('//*[@id="__next"]/div[2]/div[3]/div[2]/div[2]/div[2]/div[2]/form/div[4]/button')
    await expect(but_swp).to_be_visible()
    await but_swp.click()

# Открытие позиции
async def open_position(page: Page):
    await page.locator(
        '//*[@id="__next"]/div[1]/div[5]/div/div[2]/div/div[2]/div[2]/div[1]/div[1]/div[2]/span').click()  # Кнопка создать позицию
    await page.locator('//*[@id="__next"]/div[1]/div[5]/div/div[2]/div/div[2]/div[2]/div[2]/form/div['
                        '1]/div[1]/div/div/button').click()                                                # Отключить auto_fill
    await page.locator('//*[@id="__next"]/div[1]/div[5]/div/div[2]/div/div[2]/div[2]/div[2]/form/div['
                        '1]/div[2]/div[1]/div[2]/div[2]/div[2]').click()  # Клик на ввод max jlp
    max_price = page.locator('//*[@id="__next"]/div[1]/div[5]/div/div[2]/div/div[2]/div[2]/div[2]/form/div['
                              '3]/div[2]/div/div[3]/div[2]/div/input[2]')  # Максимальный процент
    await max_price.click(click_count=2)
    await max_price.press('Backspace')
    await max_price.fill('2.5')
    min_price = page.locator('//*[@id="__next"]/div[1]/div[5]/div/div[2]/div/div[2]/div[2]/div[2]/form/div['
                              '3]/div[2]/div/div[3]/div[1]/div/input[2]')  # Минимальный процент
    await min_price.click()
    for i in range(6):
        await min_price.press('Backspace')
    await min_price.type('0', delay=DEFAULT_DELAY)
    await page.locator(
        '//*[@id="__next"]/div[1]/div[5]/div/div[2]/div/div[2]/div[2]/div[2]/form/div[3]/div[2]/div/div[4]/div[1]').click()  # Проверка сколько транзакций
    await page.locator(
        '//*[@id="__next"]/div[1]/div[5]/div/div[2]/div/div[2]/div[2]/div[2]/form/button').click()  # Клик на кнопку создать ликвидность


# Закрытие позиции
async def close_position(page: Page):
    close_pos = page.get_by_text('USDT per JLP')
    await expect(close_pos.first).to_be_visible(timeout=20000)
    await close_pos.first.click()  # Раскрываем позицию
    withdraw_btn = page.locator(
        '//div[@class="cursor-pointer font-semibold text-base flex-shrink-0 rounded-lg px-5 py-2 text-white"]')  # Раздел вывода ликвидности
    await expect(withdraw_btn).to_be_attached(timeout=20000)
    await withdraw_btn.click()
    await page.locator(
        '//button[@class ="bg-white text-black rounded-lg p-3 border border-black/50 disabled:opacity-50 disabled:cursor-not-allowed w-full"]').click()  # Кнопка закрыть позицию

# Функция кнопки подключить кошелёк и выбора кошелька
async def connect_wallet(url: str, button: str, page: Page):
    await page.bring_to_front()
    await page.goto(url)
    wallet_connect = page.locator(button)  # Подключить кошелёк
    await wallet_connect.click()
    button_connect = page.get_by_text('Solflare')
    await button_connect.click()

# Функция парсинга баланса
async def get_balance_token(stable_coin: str, need_coin: str, page: Page):
    from_token = stable_coin.upper()
    to_token = need_coin.upper()
    input_from_token = page.locator('//*[@id="__next"]/div[2]/div[3]/div[2]/div[2]/div[2]/div[2]/form/div[1]/div['
                           '1]/div[2]/div/button/div[2]')  # первое поле для токена
    await input_from_token.click()
    await page.locator('//*[@id="__next"]/div[3]/div[1]/div/div/div[1]/input').fill(f'{token_address[from_token]}')  # первое поле для токена вводится адрес usdt
    await page.locator(
        '//*[@id="__next"]/div[3]/div[1]/div/div/div[4]/div/div/div/li/div[2]/div[2]/div[1]').click()  # клик по usdt
    input_to_token = page.locator('//*[@id="__next"]/div[2]/div[3]/div[2]/div[2]/div[2]/div[2]/form/div[1]/div['
                           '3]/div[2]/div/button/div[2]')  # второе поле для токена
    await input_to_token.click()
    await page.locator('//*[@id="__next"]/div[3]/div[1]/div/div/div[1]/input').fill(f'{token_address[to_token]}')  # во второе поле для токена вводится адрес sol
    await page.locator(
        '//*[@id="__next"]/div[3]/div[1]/div/div/div[4]/div/div/div/li/div[2]/div[2]/div[1]').click()  # клик по sol
    raw_from_token_balance = await page.locator(
        '//*[@id="__next"]/div[2]/div[3]/div[2]/div[2]/div[2]/div[2]/form/div[1]/div[1]/div[1]/div/div['
        '1]/div[2]/span[1]').inner_text()  # Парсим баланс usdt
    from_token_balance = (float(raw_from_token_balance.replace(',', '.')))
    raw_to_token_balance= await page.locator('//*[@id="__next"]/div[2]/div[3]/div[2]/div[2]/div[2]/div[2]/form/div['
                                        '1]/div[3]/div[1]/div/div[2]/span[1]').inner_text()  # Парсим баланс sol
    to_token_balance = (float(raw_to_token_balance.replace(',', '.')))
    print(f'Баланс токена {from_token} = {from_token_balance}')
    print(f'Баланс токена {to_token} = {to_token_balance}')
    return from_token_balance, to_token_balance

# Функция поиска всплывающего окна
async def find_page(context: BrowserContext, link: str) -> Page:
    pages = context.pages
    result_page = None
    for p in pages:
        if link in p.url:
            result_page = p
            break
    return result_page

# Функция подтверждения
async def wallet_functions(context: BrowserContext, button: str):
    solflare_page = await find_page(context, link='confirm_popup.html')
    if solflare_page is None:
        print("Не удалось найти всплывающее окно solflare.")
    else:
        await solflare_page.bring_to_front()
        yes_button = solflare_page.locator(button)  # Кнопка подтверждения
        await expect(yes_button).to_be_visible(timeout=20000)
        await yes_button.click(click_count=2)


# Функция процесса авторизации в кошельке
async def authorization (context: BrowserContext, seed: list, password: str):
    wallet_page = await find_page(context, link='wallet.html')
    if wallet_page is not None:
        await wallet_page.wait_for_load_state()
        await wallet_page.locator('//*[@id="root"]/div/div[2]/div/div[2]/div[2]/button').click()  # Уже есть кошелёк

        for i in range(len(seed)):
            await wallet_page.locator(f'//*[@id="mnemonic-input-{i}"]').fill(seed[i])  # перебор полей для seed

        print('Залогинились в кошельке')

        await wallet_page.locator('//*[@id="root"]/div/div[2]/div/div[2]/form/div[2]/button[2]').click()  # кнопка далее
        # -------------------- ввести пароль --------------------
        password_1 = wallet_page.locator('//*[@id=":r1:"]')  # Введите пароль
        password_2 = wallet_page.locator('//*[@id=":r2:"]')  # Повторите пароль
        checkbox = wallet_page.locator('//*[@id="root"]/div/div[2]/div/div[2]/form/div[2]/button[2]')  # Продолжить
        await expect(password_1).to_be_attached(timeout=20000)
        await password_1.fill(password)
        await password_2.fill(password)
        await checkbox.click()

        # -------------------- подтвердить секретную фразу --------------------
        await wallet_page.locator('//*[@id="root"]/div/div[2]/div/div[2]/div[2]/div/button[1]').click()  # Импортировтать
        await wallet_page.locator('//*[@id="root"]/div/div[1]/div[2]/div[2]/button/span').click()  # Продолжить
        await wallet_page.locator('//*[@id="root"]/div/div[2]/div/div[2]/button[2]/span').click()  # Вход


async def main():
    async with async_playwright() as p:
        context = await p.chromium.launch_persistent_context(
            '',
            headless=False,
            slow_mo=1000,
            args=[
                f'--disable-extensions-except={psw.SOLFLARE_EXTENSION_PATH}',
                f'--load-extension={psw.SOLFLARE_EXTENSION_PATH}',
                '--disable-blink-features=AutomationControlled',
            ],
        )

        titles = [await p.title() for p in context.pages]
        while 'Solflare' not in titles:
            titles = [await p.title() for p in context.pages]

        # Логинимся в кошельке
        await authorization(context=context, seed=psw.seed, password=psw.MM_PASSWORD)

        #   Идём на юпитер и конектим кошелёк
        jup_page = context.pages[0]
        await connect_wallet(url=jup_swap_url, button=jup_btn_con, page=jup_page)
        await wallet_functions(context=context, button=connect_button)
        # Проверяем баланс соланы
        balance_from_token, balance_to_token = await get_balance_token(stable_coin='usdt', need_coin='sol', page=jup_page)

        # Если соланы меньше 0.09 и usdt > 2, то докупаем sol на 2$
        if balance_to_token < 0.09 and balance_from_token > 2:
            await swap(page=jup_page)
            await wallet_functions(context=context, button=transaction_button)

            # Проверяем баланс jlp
        balance_from_token, balance_to_token = await get_balance_token(stable_coin='usdt', need_coin='jlp', page=jup_page)

        # Если jlp меньше 5 и usdt > 2, то докупаем jlp на 2$
        if balance_to_token < 5 and balance_from_token > 2:
            await swap(page=jup_page)
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

        await open_position(page=page)
        await wallet_functions(context=context, button=transaction_button)

        # Закрываем позицию
        await close_position(page=page)
        await wallet_functions(context=context, button=transaction_button)
        print('ОК!!!')
        await asyncio.sleep(30)
        await context.close()


if __name__ == '__main__':
    asyncio.run(main())


