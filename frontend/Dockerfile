FROM node:18-alpine

# Устанавливаем рабочую директорию
WORKDIR /app/frontend

# Копируем package.json и package-lock.json для установки зависимостей
COPY package.json package-lock.json ./

# Устанавливаем зависимости
RUN npm install --production

# Копируем весь исходный код в контейнер
COPY . .

# Создаем сборку приложения Next.js
RUN npm run build

# Указываем порт, который слушает приложение
EXPOSE 3000

# Запускаем приложение
CMD ["npm", "start"]
