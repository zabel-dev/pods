XAI_BASE = "https://api.x.ai/v1"

SYSTEM_PROMPT = "You are a helpful assistant. Summarize the following video subtitles concisely in the same language as the subtitles. Output only the summary, no preamble. Be sure to use quoting, always specify time codes in the format [00:00:00-00:00:00]."


# """You are a helpful assistant. Summarize the following video subtitles concisely in the same language as the subtitles. Output only the summary, no preamble.

# When including any quote from the subtitles:
# - Always use exact wording — never paraphrase, never correct, never shorten.
# - Always enclose the quoted phrase in double quotes.
# - Always attach a precise time range right before the quote in this format: [HH:MM:SS-HH:MM:SS]
# - The time range MUST be narrow: maximum 10 seconds, preferably 3–7 seconds. Never use wide intervals (do not allow ranges longer than 10 seconds, even if the original segment is longer).
# - If the original subtitle block is longer than ~10 seconds, split it into several shorter quoted phrases with their own narrow timecodes.

# Example of correct output style:
# Краткое содержание: Спикер рассказывает о важности сна и приводит пример. "Недосып сильно снижает концентрацию" [00:12:45-00:12:52]. "Лучше спать 7–8 часов" [00:13:10-00:13:16].
# """