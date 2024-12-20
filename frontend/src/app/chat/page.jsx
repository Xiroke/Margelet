"use client";
import React, { use, useEffect, useRef, useState } from 'react';
import { GroupItem, ChatItem, Participants, ParticipantsItem} from './_components';
import { getChats, getGroups } from './_api';
import { redirect } from 'next/navigation';
import { isAuthenticated } from '../_auth';

export default function ChatPage() {
  const user_part = [
    {id: 1, name: 'Валер Воро'},
    {id: 2, name: 'Валер Воро'},
    {id: 3, name: 'Валер Вороб'},
    {id: 4, name: 'Валер Воробeqgf'},
  ]
  const [ws, setWs] = useState(null);
  const [groups, setGroups] = useState(null);
  const [chats, setChats] = useState(null);
  const [currentGroupId, setCurrentGroupId] = useState(null);
  const [currentChatId, setCurrentChatId] = useState(null);
  const [messages, setMessages] = useState([]);
  const myMessage = useRef(null);

  useEffect(() => {
    isAuthenticated()
    getGroups().then(data => {
      setGroups(data)
    })
  }, [])

  useEffect(() => {
    if (currentGroupId) {
      getChats(currentGroupId).then(data => {
        setChats(data)
      })
    }
  }, [currentGroupId])

  useEffect(() => {
    if (!currentChatId || !currentGroupId) {
      return;
    }
    let ws;
    var token = "";
    fetch('http://localhost:8000/api/auth/get_token', {
      method: 'GET',
      credentials: 'include'
    }).then(response => response.json())
    .then(data => {
    ws = new WebSocket(`ws://127.0.0.1:8000/api/chat/${currentGroupId}/${currentChatId}?token=${data}`);
    ws.onopen = () => {
      console.log('Connected to chat:', currentChatId);
    };

    ws.onmessage = (event) => {
      setMessages(prevMessages => [...prevMessages, JSON.parse(event.data)]);
      console.log('Received message:', event.data);
    };

    ws.onclose = () => {
      console.log('Disconnected from chat:', currentChatId);
    };

    setWs(ws);

    return () => {
      if (ws) {
        ws.close();
      }
    };
    }).catch(e => {
      return redirect('/')
    })
  }, [currentChatId, currentGroupId]);
  

  const sendMessage = () => {
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(myMessage.current.value);
      myMessage.current.value = '';
    }
  };
  
  return (
    <div className='flex flex-row h-[100vh]'>
      <nav className='w-[360px] bg-[#252525] h-full pl-3 pt-6 flex flex-col gap-4'>
        <img src="/icons/menu.svg" alt="меню" className='w-10 h-10'/>
        {groups ? groups.map(item => <GroupItem key={item.id} title={item.title} subtitle={item.description} onClick={() => setCurrentGroupId(item.id)} />) : <div></div>}
      </nav>
      <main className='flex-1 flex flex-col gap-4 bg-[#141414] max-w-[1300px] px-[126px] pt-20'>
        <div className="flex flex-col gap-4">
          
          { messages ? messages.map((item, index) => <div key={index} className="bg-[#E4E4E4] text-[#252525] px-2 pt-2 pb-4 rounded-[12px] min-h-[64px] w-[456px] font-medium">{item.name}<br></br>{item.message}</div>) : <div></div>}
        </div>
        <div className="flex flex-row h-16 mt-auto mr-auto w-full ml-auto">
          <button className='flex justify-center items-center w-[80px] h-full bg-[#E4E4E4] rounded-tl-xl'><img className='rotate-45' src="/icons/attach_file.svg" alt="Прикрепить" /></button>
          <input type="text" placeholder="Написать сообщение" className='w-[746px] bg-[#E4E4E4] text-[#4D4D4D]' ref={myMessage}/>
          <button className='flex justify-center items-center w-[80px] h-full bg-[#353535] rounded-tr-xl' onClick={() => sendMessage()}><img src="/icons/send.svg" alt="отправить"/></button>
        </div>
      </main>
      <aside className="w-[400px] bg-[#252525] h-full pt-12 mr-auto px-10">
        <div className="text-center mb-6">
          <div className="w-[100px] h-[100px] bg-[#E4E4E4] rounded-[20px] mx-auto"></div>
          <div className="mt-6 text-[24px] block font-bold">Название</div>
          <div className="text-[16px] block">Описание и описание и описание...</div>
          <div className="text-[16px] text-[#4D4D4D] block">Участников: 32</div>
        </div>
        <div className="mt-[52px] flex flex-col gap-2 h-[360px]">
          <div className="font-bold text-[18px] text-[#4D4D4D] mb-2">Чаты</div>
          {chats ? chats.map(item => <ChatItem key={item.id} onClick={() => setCurrentChatId(item.id)}>{item.title}</ChatItem>) : <div></div>}
        </div>
        <Participants role='Участники' user_part={user_part}/>
      </aside>
    </div>
  );
}