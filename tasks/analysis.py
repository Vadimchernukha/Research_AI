# analysis.py
import openai
import logging

def analyze_website_content(content, prompt):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt.format(content=content)}],
            max_tokens=1000,
            temperature=0.3
        )
        output = response['choices'][0]['message']['content'].strip()
        logging.info(f"Ответ от GPT-4o-mini: {output}")
        if "+ Relevant" in output:
            if output.startswith("+ Relevant -"):
                return output.split("+ Relevant -", 1)[-1].strip()
            else:
                return output.replace("+ Relevant", "").strip()
        else:
            logging.info("Сайт не релевантен, пропускаем.")
            return None
    except Exception as e:
        logging.error(f"Ошибка в GPT-4o-mini: {e}")
        return None
