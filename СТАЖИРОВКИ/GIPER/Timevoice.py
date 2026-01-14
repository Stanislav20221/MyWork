import streamlit as st
from docx import Document
from dotenv import load_dotenv
import openai
from openai import OpenAI
import os
load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")

)
dialog = '''
    1.  Консультации по товарам (клиент хочет приобрести товар, и спрашивает отличия/характеристики/стоимость и пр).
    2.  Использование приобретённого изделия (клиент уже купил товар, и его интересуют вопросы как использовать/включить/обслуживать приобретенный товар).
    3.  Проблема, связанная с купленным товаром (консультация по изделию, если возникла какая-либо проблема, связанная с ним – не включается, что-то не работает т т.п.).
    4.  Информация о заказе (клиент хочет уточнить уточить детали заказа, например, состав, способ доставки и т. п.).
    5.  Оформление заказа (оператор оформляет заказ в разговоре).
    6.  Отмена заказа (клиент хочет отменить заказ).
    7.  Проблема, связанная с доставкой (клиент жалуется на доставку, курьер не смог связаться и пр. Все, что требует от КЦ направить запрос в ТК или логистам.).
    8.  Информация о доставке товара (клиент интересуется датой, временем и сроками доставки товара, спрашивает, где и как забрать заказ и т. п.).
    9.  Возврат/Обмен (консультации по возврату и обмену, в т.ч. звонки, которые были переданы на Отдел Клиентского Сервиса ООО "Гипер").
    10.  Адрес АСЦ (если клиента интересует адрес АСЦ, или ему нужно сдать товар на ремонт).
    11.  Закупка комплектующих АСЦ (клиента интересует вопрос покупки комплектующих, если их нельзя купить в ИМ и купить можно в АСЦ).
    12.   Нецелевой звонок (звонки, которые не попадают в ЗО КЦ ООО "Гипер").
    13.  Программа лояльности (Вопросы по программе лояльности, списаниям баллов, возвратам баллов, сертификатам, бонусам и т. п.).
    14.  Юридическое лицо (если клиент является юридическим лицом – компанией, ООО, ИП, и т. п.).
    15.  Жалоба (клиент жалуется на действия сотрудников ООО "Гипер" или Транспортных Компаний).
    16.  Рассылка/реклама (речь идет о рассылке на почту/смс/etc.)
'''
def answer_index(system, topic, dialog, temp, verbose=0):
    # Поиск релевантных отрезков из базы знаний по вопросу пользователя
    messages = [  # <-- Теперь тут 4 пробела
        {"role": "system", "content": system},
        {"role": "user", "content": f" Проанализируй текст диалога клиента м менеджера и выбери наиболее точную категорию из списка: {topic} Диалог {dialog}"}
    ]

    completion = client.chat.completions.create(  # <-- Уровень отступа теперь правильный
        model="gpt-4o-mini",
        messages=messages,
        temperature=temp
    )
    answer = completion.choices[0].message.content
    return answer


st.title("Определение темы обращения клиента")
# Создание боковой панели
st.sidebar.header("Настройки модели")
temp = st.sidebar.slider("Температура", min_value=0.0, max_value=2.0, value=0.1) 
if "custom_css" not in st.session_state:
    st.session_state.custom_css = True  # Флаг, что CSS уже применён
    custom_text = "Перетащите файл сюда или выберите его вручную"
    st.markdown(f"""
        <style>
            .stFileUploader div div {{ visibility: hidden; }}
            .stFileUploader div div:after {{
                content: "{custom_text}";
                visibility: visible;
                display: block;
                text-align: center;
                font-size: 16px;
                color: #4F8BF9;
                font-weight: bold;
            }}
        </style>
    """, unsafe_allow_html=True)

st.sidebar.header("Загрузить файл")
uploaded_file = st.sidebar.file_uploader("Выберите файл для загрузки")
#if st.sidebar.button('Выбрать файл'):
 #   uploaded_file = st.sidebar.file_uploader("Пожалуйста, выберите файл", type=['docx'], key="file_uploader")

if uploaded_file is not None:
    st.success("Диалог успешно загружен!")
    if uploaded_file.name.endswith('.docx'):
       doc = Document(uploaded_file)
       content = "\n".join([para.text for para in doc.paragraphs])
   #    st.text_area("Содержимое файла:", content, height=300)           
    
#user_input = st.text_area("Введите ваше сообщение:", "")
    if st.button("Анализировать диалог"):
        system = "Ты — виртуальный ассистент в магазине. Твоя задача — четко определить тему звонка покупателя на основе его обращения."
        topic = content
        st.write(answer_index(system, topic, dialog, temp))
else:
    if st.button("Анализировать диалог"):
        st.write("Неоюбходимо выбрать файл для анализа")
