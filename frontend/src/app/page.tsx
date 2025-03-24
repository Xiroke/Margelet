'use client';
import { useEffect } from 'react';
import './styles.css';
import { simpleNavigate } from '@/features/redirect';

export default function Home() {
  async function onSubmit(e) {
    e.preventDefault();

    const formData = new FormData(e.target);
    const user = {
      email: formData.get('email'),
      password: formData.get('password'),
    };

    const response = await fetch(`${process.env.NEXT_PUBLIC_API_PATH}/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      credentials: 'include',
      body: new URLSearchParams(user),
    });

    if (response.status == 200) {
      simpleNavigate('/chat');
    }
  }

  useEffect(() => {
    const drop = document.querySelector('.floating-drop');

    setInterval(() => {
      const newColor = `rgba(${Math.random() * 255}, ${Math.random() * 100 + 155}, ${
        Math.random() * 255
      }, 0.5)`;
      drop.style.boxShadow = `0 0 30px 15px ${newColor}`;
    }, 2000);
  }, []);
  return (
    <>
      <div className="wrapper">
        <form action="" onSubmit={onSubmit}>
          <h1>Вход</h1>
          <div className="input-box">
            <input type="text" name="email" placeholder="email" required />
            <i className="bx bx-user-check"></i>
          </div>
          <div className="input-box">
            <input type="text" name="password" placeholder="Пароль" required />
            <i className="bx bx-key"></i>
          </div>

          <div className="remember">
            <label htmlFor="">
              <input type="checkbox" />
              Запомнить меня
            </label>
            <a href="#">Забыли пароль?</a>
          </div>

          <button type="submit" className="btn">
            Войти
          </button>

          <div className="register-link">
            <p>
              Если у вас нет аккаунта* <a href="/registrate">Регистрация</a>
            </p>
          </div>
        </form>
      </div>

      <div className="background-animation">
        <div className="floating-drop"></div>
      </div>
      <div className="background-animation">
        <div className="floating-drop2"></div>
      </div>
    </>
  );
}
