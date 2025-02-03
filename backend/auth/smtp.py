from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import aiosmtplib

from config import settings


async def send_message(to, subject, text):
	msg = MIMEMultipart()
	msg['Subject'] = subject
	msg['from'] = settings.SMTP_USER
	msg['to'] = to

	msg.attach(MIMEText(text, 'plain'))

	server = aiosmtplib.SMTP(hostname=settings.SMTP_HOST, port=settings.SMTP_PORT)
	await server.connect()
	await server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
	await server.send_message(msg)  # Отправка сообщения
	await server.quit()  # Закрываем соединение
