import asyncio
from playwright.async_api import async_playwright, expect
import wallet_settings as psw

DEFAULT_DELAY = 300


async def main():
    async with async_playwright() as p:
        context = await p.chromium.launch_persistent_context(
            '',
            headless=False,
            args=[
                f'--disable-extensions-except={psw.METAMASK_EXTENSION_PATH}',
                f'--load-extension={psw.METAMASK_EXTENSION_PATH}',
                '--disable-blink-features=AutomationControlled',
            ],
        )


        titles = [await p.title() for p in context.pages]
        while 'Solflare' not in titles:
            titles = [await p.title() for p in context.pages]

        mm_page = context.pages[1]
        await mm_page.wait_for_load_state()
        await asyncio.sleep(5)

        my_wallet_btn = mm_page.locator('//*[@id="root"]/div/div[2]/div/div[2]/div[2]/button')
        await my_wallet_btn.click()


        for i in range(len(psw.seed)):

            await mm_page.locator(f'//*[@id="mnemonic-input-{i}"]').fill(psw.seed[i])
        print('Залогинились в кошельке')

        continue_btn = mm_page.locator('//*[@id="root"]/div/div[2]/div/div[2]/form/div[2]/button[2]')
        await continue_btn.click()
        await asyncio.sleep(3)
        # -------------------- ввести пароль --------------------
        passwd_1 = mm_page.locator('//*[@id=":r1:"]')
        passwd_2 = mm_page.locator('//*[@id=":r2:"]')
        checkbox = mm_page.locator('//*[@id="root"]/div/div[2]/div/div[2]/form/div[2]/button[2]')
        await expect(passwd_1).to_be_attached()
        await passwd_1.fill(psw.MM_PASSWORD)
        await passwd_2.fill(psw.MM_PASSWORD)
        await checkbox.click()

        # -------------------- подтвердить секретную фразу --------------------
        seed_field = mm_page.locator('//*[@id="root"]/div/div[2]/div/div[2]/div[2]/div/button[1]')
        await seed_field.click()
        seed_field2 = mm_page.locator('//*[@id="root"]/div/div[1]/div[2]/div[2]/button/span')
        await seed_field2.click()
        seed_field3 = mm_page.locator('//*[@id="root"]/div/div[2]/div/div[2]/button[2]/span')
        await seed_field3.click()

        # -------------------- новую страничку --------------------
        mm_page_0 = context.pages[0]

        await asyncio.sleep(5)

        async def ballance_wallet(page):
            await page.bring_to_front()
            await page.goto(psw.swap_url)
            walconect = page.locator('//*[@id="__next"]/div[2]/div[1]/div/div[4]/div[3]/div/button[2]/div/span[2]')
            await walconect.click()
            butnconect = page.get_by_text('Solflare')
            await butnconect.click()
            await asyncio.sleep(4)
            pages = page.context.pages
            solflare_popup = None
            for p in pages:
                if 'confirm_popup.html' in p.url and p.url != page.url:
                    solflare_popup = p
                    break
            if solflare_popup:
                await solflare_popup.bring_to_front()
                conect_jup = solflare_popup.locator('//html/body/div[2]/div[2]/div/div[3]/div/button[2]')
                await conect_jup.click()
            else:
                print("Не удалось найти всплывающее окно solflare.")
            await asyncio.sleep(5)

            token_1 = page.locator('//*[@id="__next"]/div[2]/div[3]/div[2]/div[2]/div[2]/div[2]/form/div[1]/div[1]/div[2]/div/button/div[2]')
            await token_1.click()
            await page.locator('//*[@id="__next"]/div[3]/div[1]/div/div/div[1]/input').fill('Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB')
            await page.locator('//*[@id="__next"]/div[3]/div[1]/div/div/div[4]/div/div/div/li/div[2]/div[2]/div[1]').click()
            token_2 = page.locator('//*[@id="__next"]/div[2]/div[3]/div[2]/div[2]/div[2]/div[2]/form/div[1]/div[3]/div[2]/div/button/div[2]')
            await token_2.click()
            await page.locator('//*[@id="__next"]/div[3]/div[1]/div/div/div[1]/input').fill('So11111111111111111111111111111111111111112')
            await page.locator('//*[@id="__next"]/div[3]/div[1]/div/div/div[4]/div/div/div/li/div[2]/div[2]/div[1]').click()

            ballance_sol_1 = page.locator('//*[@id="__next"]/div[2]/div[3]/div[2]/div[2]/div[2]/div[2]/form/div[1]/div[3]/div[1]/div/div[2]/span[1]')
            ballance_sol_2 = await ballance_sol_1.inner_text()
            ballance_sol = (float(ballance_sol_2.replace(',','.')))
            print(ballance_sol)

            # Проверка, если баланс соланы больше, то докупаем ещё
            if ballance_sol > 0.05:
                await page.locator('//*[@id="__next"]/div[2]/div[3]/div[2]/div[2]/div[2]/div[2]/form/div[1]/div[1]/div[2]/span/div/input').fill('2')
                but_swp = page.locator('//*[@id="__next"]/div[2]/div[3]/div[2]/div[2]/div[2]/div[2]/form/div[4]/button')
                await expect(but_swp).to_be_visible()
                await but_swp.click()
                await asyncio.sleep(3)
                pages = page.context.pages
                solflare_popup = None
                for p in pages:
                    if 'confirm_popup.html' in p.url and p.url != page.url:
                        solflare_popup = p
                        break
                if solflare_popup:
                    await solflare_popup.bring_to_front()
                    await asyncio.sleep(3)
                    tranz_yes = solflare_popup.locator('//html/body/div[2]/div[2]/div/div[2]/div/div[2]/div[2]/div[2]/button[2]')
                    await tranz_yes.click()
                else:
                    print("Не удалось найти всплывающее окно solflare.")
                await asyncio.sleep(5)
            await asyncio.sleep(7777)
        page = mm_page_0
        await ballance_wallet(page)





        mm_page_0 = context.pages[0]
        # Подключение кошелька
        async def connect_wallet(page):
            await page.bring_to_front()
            await page.goto(psw.page_url)

            await asyncio.sleep(10)
            butnconect = page.locator('//button[contains(@class, "bg-[#191C32]")]')
            await butnconect.click()
            await asyncio.sleep(5)
            walletconect = page.locator('//span[@class ="css-1wq1rs1" and text()="Solflare"]')
            await walletconect.click()
            await asyncio.sleep(5)

            # walletconect = page.locator('/html/body/div[2]/div[2]/div/div[3]/div/button[2]/span')
            # await walletconect.click()
            # await asyncio.sleep(3)



            # Ждем всплывающее окно MetaMask
            await asyncio.sleep(2)
            pages = page.context.pages
            metamask_popup = None
            for p in pages:
                if 'confirm_popup.html' in p.url and p.url != page.url:
                    metamask_popup = p
                    break
            if metamask_popup:
                await metamask_popup.bring_to_front()
                await metamask_popup.locator('//html/body/div[2]/div[2]/div/div[3]/div/button[2]/span').click()
                await metamask_popup.close()
            else:
                print("Не удалось найти всплывающее окно MetaMask.")
            await asyncio.sleep(2)


        page = mm_page_0  # Получаем первую открытую страницу

        await connect_wallet(page)



        # ТЕСТОВАЯ работа с сайтом
        inputs = page.locator('//*[@id="__next"]/div[1]/div[5]/div/div[2]/div[2]/div/div[1]/div/div/input')
        await expect(inputs.first).to_be_visible(timeout=20000)
        await inputs.first.type('jlp', delay=DEFAULT_DELAY)
        await asyncio.sleep(2)
        try:
            inputs2 = page.get_by_text('JLP-USDT', exact=True)
            await expect(inputs2.first).to_be_visible()
            await inputs2.first.scroll_into_view_if_needed()
            await inputs2.first.click()
        except Exception as e:
            print(f'Искомой пары нет: {e}')
            await context.close()

        await asyncio.sleep(5555555)
        await context.close()
        print('ОК!!!')

if __name__ == '__main__':
    asyncio.run(main())
