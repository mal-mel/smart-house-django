import requests

url = 'https://docs.google.com/forms/d/1HfY7fxrvt6QSIqwz0ctRbwcd8WtqvRsiQxrhP6xiblo/edit?usp=forms_home&amp;ths=true'
r = requests.post(url, data={
    'entry.1180008447': 'Есть ребенок',
    'entry.1332036666': '25-35',
    'entry.129690719': 'Москва, Санкт-Петербург',
    'entry.1358177935': 'Высшее',
    'entry.892508344': '25-35',
    'entry.1701846148': 'Могу позволить себе средние покупки ( телевизор, смартфон)'
})
