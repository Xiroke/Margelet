"use client"
import {useEffect} from "react";
import { redirect } from "next/navigation";
import "./logstyle.css"
import { isLogined } from "./_auth";

export default function Home() {
    async function onSubmit(e){
        e.preventDefault()

        const formData = new FormData(e.target); // Получаем данные формы
        const user = {
          username: formData.get('email'),
          password: formData.get('password'),
        };

        await fetch('http://127.0.0.1:8000/api/auth/login', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
          },
          credentials: 'include',
          body: new URLSearchParams(user).toString(), // Преобразуем объект в строку JSON
        })
          .then(response => redirect('/chat'))
          .catch(error => console.error('Ошибка:', error));

        
    }

  useEffect(() => {
    isLogined()
    const drop = document.querySelector('.floating-drop');

    setInterval(() => {
        const newColor = `rgba(${Math.random() * 255}, ${Math.random() * 100 + 155}, ${Math.random() * 255}, 0.5)`;
        drop.style.boxShadow = `0 0 30px 15px ${newColor}`;
    }, 2000);

}, [])
  return (
    <>
    <div className="reg">
      <div className="wrapper">
          <form action="" onSubmit={onSubmit}>
              <h1>Вход</h1>
              <div className="input-box"> 
                  <input type="text" name="email" placeholder="email" required />
                  <i className='bx bx-user-check'></i>
              </div>
              <div className="input-box">
                  <input type="text" name="password" placeholder="Пароль" required />
                  <i className='bx bx-key'></i>
              </div>

              <div className="remember">
                  <label htmlFor=""> 
                      <input type="checkbox"/>
                      Запомнить меня
                  </label>
                  <a href="#">Забыли пароль?</a>
              </div>

              <button type="submit" className="btn">Войти</button>

              <div className="register-link">
                  <p>Если у вас нет аккаунта* <a href="http://127.0.0.1:3000/registrate">Регистрация</a></p>
              </div>
          </form>
      </div>
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
