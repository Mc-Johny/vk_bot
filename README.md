# Школьный бот
Задача бота заключается в том, что дает расписание человеку на завтрашний день нажав на кнопку.

Расписание выдает либо картинкой:

<img src="https://sun9-20.userapi.com/c857724/v857724455/1ff0f8/2iG8NYyYFd8.jpg" width="200">

Либо текстом:

<img src="https://sun9-50.userapi.com/c857432/v857432455/1f2f45/nUcsgWVHdmg.jpg" width="200">

Прежде чем выдать картинку/текст, бот отправляет запрос к api сайта openweathermap.<br>
После этого обращается в базу данных, где берет предметы на завтрашний день.<br>
<hr>
А вот с картинкой уже чуток посложнее.<br>
Используя библиотеку Pillow генерируется изображение с текстом(Предметы и погода).<br>
Чтобы хорошо видеть текст на любом изображении используется технология контрастирующих цветов.<br>
Берется область под текст, определяется часто встречающийся цвет и потом уже из белого цвета вычитаем этот самый цвет.<br>
<b>Profit</b>
