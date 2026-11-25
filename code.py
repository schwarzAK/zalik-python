def estimate_cost(input_tokens, output_tokens, price_in, price_out, requests=1):
    """Оцінює вартість запитів до LLM у доларах.

    Ціни задаються у доларах за 1 мільйон токенів.
    """
    # Перевіряємо, що жодне значення не від'ємне
    if min(input_tokens, output_tokens, price_in, price_out, requests) < 0:
        raise ValueError("Значення не можуть бути від'ємними")

    # Вартість одного запиту: вхідні токени + вихідні токени
    cost_in = input_tokens / 1_000_000 * price_in
    cost_out = output_tokens / 1_000_000 * price_out
    one_request = cost_in + cost_out

    # Множимо на кількість запитів і округлюємо до центів
    return round(one_request * requests, 2)


if __name__ == "__main__":
    # Приклад: 10 000 запитів, 900 токенів на вході та 200 на виході
    total = estimate_cost(900, 200, price_in=0.10, price_out=0.50, requests=10_000)
    print(f"Загальна вартість: ${total}")