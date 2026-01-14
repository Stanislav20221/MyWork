from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from langchain.text_splitter import MarkdownHeaderTextSplitter
from selenium.common.exceptions import StaleElementReferenceException
import time
start_time = time.time()
# Запуск драйвера
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)

driver.get("https://academydpo.org/karta-sajta")
time.sleep(2)

stop_list = {
    "8 (800) 707-71-91", "info@academydpo.org", "Отзывы", "Стать нашим партнером",
    "РАБОТАЕМ В СООТВЕТСТВИИ С ФЕДЕРАЛЬНЫМИ ЗАКОНАМИ №44-Ф3 И №223-Ф3", "Проверить лицензию",
    "Whatsapp", "Telegram", "Главная", "Об Академии", "Партнерство", "Акции", "Контакты",
    "Проверить документ", "Вопрос / Ответ", "Академия ДПО", "Сведения об образовательной организации",
    "Все направления", "Портал обучения", "Лицензии и документы", "Основные сведения",
    "Ответы на часто задаваемые вопросы", "Оплата образовательных услуг",
    "Стипендии и иные виды материальной поддержки", "Финансово-хозяйственная деятельность",
    "Вакантные места для приема (перевода)", "Материально-техническое обеспечение и оснащенность",
    "Все направления обучения", "Сотрудники"
}

def clean_text(text: str) -> str:
    text = text.strip()
    if not text or text.isdigit() or len(text) <= 1 or text in stop_list:
        return ""
    return text
#-------------------------------------------------------------------------------функция разбиения текста на чанки------------------------------------------------------------------------------------------------------------------------------------------------
def markdawn_text(text:str):

    headers_to_split_on = [
        ("#", "h1"),
        ("##", "h2"),
    ]
    markdown_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=headers_to_split_on)
    fragments = markdown_splitter.split_text(text)
    return fragments


#-------------------------------------------------------------------------------функция определения заголовков----------------------------------------------------------------------------------------------------------------------------------------------------
def is_header(text: str, href: str) -> bool:
    """Определение: заголовок ли это"""
    # Ключевые слова и короткий текст — скорее всего заголовок
    keywords = ["дело", "направление", "обучение", "образование", "менеджмент", "экономика"]
    if any(word.lower() in text.lower() for word in keywords) and len(text) < 40:
        return True
    # Или если в ссылке нет подкатегорий (нет / внутри)
    if href.count("/") <= 4:
        return True
    return False
#------------------------------------------------------------------------------------Удаление повторяющеейся информации из текста-------------------------------------------------------------------------------------------------------------------------------
def remove_duplicates(lines: list[str]) -> list[str]:
    seen = set()
    result_lines = []
    for line in lines:
        line = line.strip()
        if line and line not in seen:
            seen.add(line)
            result_lines.append(line)
    return result_lines
results = []

for link in driver.find_elements(By.CSS_SELECTOR, "a"):
    try:
        text = clean_text(link.text or "")
        href = link.get_attribute("href")
        if not text or not href:
            continue
        if is_header(text, href):
            results.append(f"# {text}")
        else:
            results.append(f"## {text}")
    except StaleElementReferenceException:
        continue

driver.quit()

# Запись в файл
with open("raw_method2.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(remove_duplicates(results)))

with open("raw_method2.txt", "r", encoding="utf-8") as fr:
    content = fr.read()

chanks = markdawn_text(content)
with open("converted_method2.md", "w", encoding="utf-8") as fmd:
    fmd.write(content)
#------------------------------------------------------------------------------------Выводим время работы программы-------------------------------------------------------------------------------------------------------------------------------------------------
end_time = time.time()
elapsed_time = end_time - start_time
print(f"Время работы программы: {elapsed_time:.2f} секунд")