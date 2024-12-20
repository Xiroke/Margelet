"use client"
import Image from "next/image";
import {useEffect} from "react"
import './style.css' 

export default function Home() {
    function onSubmit(e){
        e.preventDefault(); // Исправлено

        const formData = new FormData(e.target); // Получаем данные формы
        const user = {
          name: formData.get('username'),
          email: formData.get('email'),
          password: formData.get('password'),
        };
    
        // Отправляем данные на сервер
        fetch('http://127.0.0.1:8000/api/auth/register', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(user), // Преобразуем объект в строку JSON
        })
          .then(response => response.json())
          .then(data => {
            if (data.status === 201) {
              alert("Регистрация прошла успешно!");
            } else {
              alert("Ошибка регистрации");
            }
          })
          .catch(error => console.error('Ошибка:', error));
    }

    useEffect(() => {
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
                <h1>Регистрация</h1>
                <div className="input-box"> 
                    <input type="text" name="name" placeholder="Имя пользователя" required />
                    <i className='bx bx-user-check'></i>
                </div>
                <div className="input-box"> 
                    <input type="text" name="email" placeholder="Email" required />
                    <i className='bx bx-envelope' ></i>
                </div>
                <div className="input-box">
                    <input type="text" name="password" placeholder="Пароль" required />
                    <i className='bx bx-key'></i>
                </div>

                <div className="input-box">
                    <input type="text" placeholder="Повторите пароль" required />
                    <i className='bx bx-key'></i>
                </div>

                <div className="remember">
                    <label for=""> 
                        <input type="checkbox" />
                        Запомнить меня
                    </label>
                </div>

                <button type="submit" className="btn">Зарегистрироваться</button>

                <div className="register-link">
                    <p>Если у вас уже есть аккаунт* <a href="http://127.0.0.1:3000/">Вход</a></p>
                </div>

            </form>
            </div>
        </div>

        <div className="background-animation">
            <div className="floating-drop"></div>
        </div>

        </>
    );
}
