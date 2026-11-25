def estimate_cost(input_tokens, output_tokens, price_in, price_out, requests=1):
    """Estimates the cost of LLM requests in US dollars.

    Prices are given in dollars per 1 million tokens.
    """
    # Make sure no value is negative
    if min(input_tokens, output_tokens, price_in, price_out, requests) < 0:
        raise ValueError("Values must not be negative")

    # Cost of one request: input tokens + output tokens
    cost_in = input_tokens / 1_000_000 * price_in
    cost_out = output_tokens / 1_000_000 * price_out
    one_request = cost_in + cost_out

    # Multiply by the number of requests and round to cents
    return round(one_request * requests, 2)


if __name__ == "__main__":
    # Example: 10,000 requests, 900 input tokens and 200 output tokens
    total = estimate_cost(900, 200, price_in=0.10, price_out=0.50, requests=10_000)
    print(f"Total cost: ${total}")