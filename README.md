Для работы сервиса необходимы необходимы:
    Интерпретатор python3.6
    Мененджер пакетов pip
    База данных mysql
    Сервер nginx

Настройка сервиса:
    Клонируйте данный репозиторий себе на машину
    Устновите virtualenv
    ```pip install virtualenv```
    Перейдите в созданную директорию
    ```cd YaBackSchool```
    Создайте новое виртуальное окружение
    ```virtualenv env```
    Ативируйте его
    ```source env/bin/activate```
    Устновите зависимости
    ```pip install -r requirements.txt```
    
    Настраиваем базу данных
    Любым удобным вам способом подключитесь к базе данных, например:
    ```mysql -u root -p```
    Создайте нового пользователя. Для этого выполните следующие запросы.
    ```CREATE USER 'YaBack'@'localhost' IDENTIFIED BY 'Your_Password48';
    GRANT ALL PRIVILEGES ON * . * TO 'YaBack'@'localhost';
    FLUSH PRIVILEGES;
    ```
    Примечание:
    Вместо YaBack укажите имя пользователя, вместо Your_Password48 пароль
    Следующие команды создадут новую базу данных и необходимые таблицы 
    ```
    CREATE DATABASE `imports` CHARACTER SET utf8 COLLATE utf8_general_ci;
    use imports;
    create table `imports` ( id int auto_increment, constraint imports_pk primary key (id) );
    ```
   Откройте config.py и впишите ваши логин и пароль, которые вы указали на при создании нового пользователя в mysql
   
   Уже сейчас сервис можно запускать
   ```python3 run.py```
   Теперь настроим uWSGI и nginx
   Установите nginx:
   ```sudo apt-get install nginx```
   Добавим сервис в автозагрузку:
   Примечание: 
   Вместо /home/entrant используйте путь к директории, в которую вы клонировали проект
   Необходимо создать несколько файлов. Вместо редактора vim можно использовать любой другой редактор. Например, nano
   ```sudo vim /etc/systemd/system/YaBackSchool.service```
   Добавьте следующие строки:
   ```
    [Unit]
    Description=wsgi for YaBackSchool
    After=network.target
    [Service]
    User=entrant
    Group=www-data
    WorkingDirectory=/home/entrant/YaBackSchool
    Environment="PATH=/home/entrant/YaBackSchool/env/bin"
    ExecStart=/home/entrant/YaBackSchool/env/bin/uwsgi --ini YaBackSchool.ini
    [Install]
    WantedBy=multi-user.target
   ```
   Включаем сервис и добавляем автозагрузку
   ```
   systemctl start yandex_backend_school
   systemctl enable yandex_backend_school
   ```   
   Настроиваем nginx:
   ```sudo vim /etc/nginx/sites-available/YaBackSchool```
   Добавляем следующие строки:
   ```
    server {
        listen 0.0.0.0:8080;
        location / {
            client_max_body_size 5000M;
            client_body_buffer_size 50000k;
            include uwsgi_params;
            uwsgi_pass unix:/home/entrant/yandex_backend_school_2nd/yandex_backend_school.sock;
        }
    }
   ```
   И включаем наш сервис
   ```ln -s /etc/nginx/sites-available/yandex_backend_school /etc/nginx/sites-enabled```
   Перезапускаем сервис
   ```systemctl restart nginx```
   
Запуск тестов:
    Запустите сервис
    Установите pytest:
    ```sudo apt install python3-pytest```
    В директории проекта выполните:
    ```pytest-3```