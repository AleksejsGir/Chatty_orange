#!/bin/bash

# Domains для сертификата (через пробел)
domains=(chattyorange.eu www.chattyorange.eu)
email="chattyorangeeu@gmail.com"
staging=0 # Установите 1 для тестирования сертификата

if [ -d "./certbot" ]; then
  read -p "Существующие данные сертификата найдены. Продолжить и перезаписать существующие сертификаты? (y/N): " decision
  if [ "$decision" != "Y" ] && [ "$decision" != "y" ]; then
    exit
  fi
fi

# Создаем директории для certbot
mkdir -p ./certbot/conf/live/${domains[0]}
mkdir -p ./certbot/www

# Запускаем nginx для проверки домена
docker compose -f docker-compose.prod.yml up --force-recreate -d nginx

# Остановим существующий certbot контейнер
docker compose -f docker-compose.prod.yml stop certbot

# Проверка доступности порта 80
echo "Проверка доступности порта 80..."
sleep 5

# Получаем новые сертификаты
echo "### Получение сертификатов Let's Encrypt..."

if [ $staging != "0" ]; then
  staging_arg="--staging"
else
  staging_arg=""
fi

docker compose -f docker-compose.prod.yml run --rm --entrypoint "\
  certbot certonly --webroot -w /var/www/certbot \
    $staging_arg \
    --email $email \
    --rsa-key-size 4096 \
    --agree-tos \
    --no-eff-email \
    -d ${domains[0]} -d ${domains[1]}" certbot

# Перезапускаем nginx для загрузки SSL конфигурации
docker compose -f docker-compose.prod.yml exec nginx nginx -s reload