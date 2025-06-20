from playwright.sync_api import sync_playwright
from scrapy.selector import Selector
import time

# URL категории
url = "https://lu.ru/sortament/lyustri/" 

with sync_playwright() as p:
    # Запуск браузера (можно использовать 'firefox' или 'webkit')
    browser = p.firefox.launch(headless=True)
    page = browser.new_page()

    print("Открываем страницу...")
    page.goto(url)

    # Ждём загрузки товаров (можно улучшить через ожидание элемента)
    print("Ждём подгрузки товаров...")
    time.sleep(5)  # лучше заменить на WebDriverWait-style ожидание

    # Получаем полный HTML страницы
    html = page.content()
    browser.close()

    # Сохраняем HTML локально для проверки
    with open("lu_ru_category.html", "w", encoding="utf-8") as f:
        f.write(html)

    print("Парсим данные...")

    # Используем Scrapy-селектор для обработки HTML
    selector = Selector(text=html)

    # # Пример селекторов — замени на актуальные, если структура отличается
    # for product in selector.css("div.product-name-block"):
    #     name = product.css("div.name_good_item::text").get(default="").strip()
    #     price = product.css("div.new-price::text").get(default="").strip()
    #     link = product.css("a::attr(href)").get()

    for product in selector.css("div.product-block"):
        name = product.css("span.name_good_item::text").get(default="").strip()
        price = product.css("div.new-price span::text").get(default="").strip()
        old_price = product.css("div.old-price::text").get(default="").strip()
        link = product.css("a.product-name::attr(href)").get()

        if link and not link.startswith("http"):
            link = f"https://lu.ru{link}" 

        print({
            "name": name,
            "price": price,
            "old_price": old_price,
            "url": link
        })

    import csv

    with open("lu_ru_products.csv", "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["name", "price", "old_price", "url"])
        writer.writeheader()
        for product in selector.css("div.product-block"):
            name = product.css("span.name_good_item::text").get(default="").strip()
            price = product.css("div.new-price span::text").get(default="").strip()
            old_price = product.css("div.old-price::text").get(default="").strip()
            link = product.css("a.product-name::attr(href)").get()
            if link and not link.startswith("http"):
                link = f"https:{link}"
            writer.writerow({
                "name": name,
                "price": price,
                "old_price": old_price,
                "url": link
            })