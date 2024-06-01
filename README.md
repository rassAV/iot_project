# iot_project

Инструкция по эксплуатации устройства:

Подготовительный этап:

1) Узнать ip сети wifi командой ipconfig (в консоли cmd)

2) Изменить IP_SERVER в файле скетча config.h на ip сети wifi

3) Запустить сервер в сети wifi

4) Закачать sketch на esp и нажимать reset

5) Подключить есп к схеме, подать питание

Использование устройства:

1) Подключиться к точке доступа есп и перейти в браузере на веб-форму по ip 192.168.99.34

2) Ввести логин и пароль сети wifi, в которой запущен сервер и отправить данные (кнопка send)

3) Есп подключается к wifi и переходит в режим ожидания

4) Нажать кнопку один раз, чтобы данные с датчика воздуха начали отправляться на сервер и записываться в базу данных

Состояния устройства:

красный - раздаёт точку доступа

красный (мигает) - подключение к сети wifi

жёлтый - связь с сервером установлена, ожидание

зелёный - отправка данных на сервер
