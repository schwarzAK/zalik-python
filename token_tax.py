import sys
from pathlib import Path

try:
    import tiktoken
except ImportError:
    sys.exit("Спочатку встановіть бібліотеку: pip install tiktoken")

FOLDER = Path(__file__).resolve().parent

ENC = tiktoken.get_encoding("o200k_base")

MATERIALS = [
    ("Абзац", "UA", "ua_paragraph.txt"),
    ("Абзац", "EN", "en_paragraph.txt"),
    ("JSON-запит студента", "UA", "data.json"),
    ("Python-код (коментарі UA)", "UA", "code.py"),
    ("Python-код (коментарі EN)", "EN", "code_en.py"),
    ("Системний промпт", "UA", "bot_system_prompt_ua.txt"),
    ("Системний промпт", "EN", "bot_system_prompt_en.txt"),
    ("Питання бота", "UA", "bot_question_ua.txt"),
    ("Питання бота", "EN", "bot_question_en.txt"),
    ("Відповідь бота", "UA", "bot_answer_ua.txt"),
    ("Відповідь бота", "EN", "bot_answer_en.txt"),
]

PAIRS = {
    "ua_paragraph.txt": "en_paragraph.txt",
    "code.py": "code_en.py",
    "bot_system_prompt_ua.txt": "bot_system_prompt_en.txt",
    "bot_question_ua.txt": "bot_question_en.txt",
    "bot_answer_ua.txt": "bot_answer_en.txt",
}


SCENARIO_REQUESTS = 10_000
MODELS = [
    ("gpt-6-luna", 0.10, 0.50, 1.0),
    ("gemini-3.5-flash-lite", 0.30, 2.50, 1.0),
    ("Claude Fable 5.2", 8.0, 40.0, 1.0),
    ("Claude Fable 5.2 (чутливість ×1.3)", 8.0, 40.0, 1.3),
]


def read_file(name):
    with open(FOLDER / name, encoding="utf-8", newline="") as f:
        return f.read()


def count(name):
    text = read_file(name)
    chars = len(text)
    words = len(text.split())
    tokens = len(ENC.encode(text))
    return chars, words, tokens


def estimate_cost(input_tokens, output_tokens, price_in, price_out, requests=1):
    """Вартість запитів у доларах (ціни за 1 млн токенів)"""
    one_request = (input_tokens / 1_000_000 * price_in
                   + output_tokens / 1_000_000 * price_out)
    return one_request, one_request * requests


def print_token_table(results, results_by_file):
    print("\nТАБЛИЦЯ ТОКЕНІВ")
    header = (f"{'Матеріал':<28}{'Мова':<6}{'Символів':>9}{'Слів':>7}"
              f"{'Токенів':>9}{'Тк/слово':>10}{'Сим/тк':>8}{'× до EN':>9}")
    print(header)
    print("-" * len(header))
    for (label, lang, fname), (chars, words, tokens) in results.items():
        per_word = tokens / words if words else 0
        per_token = chars / tokens if tokens else 0
        ratio = ""
        if fname in PAIRS:
            en_tokens = results_by_file[PAIRS[fname]][2]
            ratio = f"{tokens / en_tokens:.2f}"
        print(f"{label:<28}{lang:<6}{chars:>9}{words:>7}{tokens:>9}"
              f"{per_word:>10.2f}{per_token:>8.2f}{ratio:>9}")


def print_scenario(results_by_file):
    print("\nСЦЕНАРІЙ: чат-бот кафедри, 10 000 запитів на місяць")
    print("input = системний промпт + питання, output = відповідь\n")
    header = (f"{'Модель':<36}{'Мова':<6}{'Tk input':>9}{'Tk output':>10}"
              f"{'$ за запит':>12}{'$ на місяць':>13}{'з input $':>11}{'з output $':>12}")
    print(header)
    print("-" * len(header))

    for model, p_in, p_out, mult in MODELS:
        monthly_by_lang = {}
        for lang, sys_f, q_f, a_f in [
            ("UA", "bot_system_prompt_ua.txt", "bot_question_ua.txt", "bot_answer_ua.txt"),
            ("EN", "bot_system_prompt_en.txt", "bot_question_en.txt", "bot_answer_en.txt"),
        ]:
            tok_in = round((results_by_file[sys_f][2] + results_by_file[q_f][2]) * mult)
            tok_out = round(results_by_file[a_f][2] * mult)
            one, monthly = estimate_cost(tok_in, tok_out, p_in, p_out, SCENARIO_REQUESTS)
            cost_in = tok_in / 1_000_000 * p_in * SCENARIO_REQUESTS
            cost_out = tok_out / 1_000_000 * p_out * SCENARIO_REQUESTS
            monthly_by_lang[lang] = monthly
            print(f"{model:<36}{lang:<6}{tok_in:>9}{tok_out:>10}"
                  f"{one:>12.5f}{monthly:>13.2f}{cost_in:>11.2f}{cost_out:>12.2f}")

        ua, en = monthly_by_lang["UA"], monthly_by_lang["EN"]
        if en:
            tax = (ua / en - 1) * 100
            print(f"{'':<36}UA/EN = {ua / en:.2f}, «податок на українську» = {tax:.1f}%\n")


if __name__ == "__main__":
    results_by_file = {}
    results = {}
    for label, lang, fname in MATERIALS:
        results_by_file[fname] = count(fname)
        results[(label, lang, fname)] = results_by_file[fname]

    print_token_table(results, results_by_file)
    print_scenario(results_by_file)
    print("\nУВАГА: токени рахуються токенізатором OpenAI. Для Gemini і Claude це наближення.")
