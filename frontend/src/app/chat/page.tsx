'use client';
import React, { useEffect, useRef, useState } from 'react';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import {
  IconSearch,
  IconPaperclip,
  IconMenu2,
  IconMessagePlus,
  IconCodePlus,
  IconTransferOut,
} from '@tabler/icons-react';
import Image from 'next/image';
import 'react-image-crop/dist/ReactCrop.css';
import './styles.css';

import {
  useChatsSWR,
  useGroupsSWR,
  useTokenSWR,
  useUsersMeSWR,
  fetchAllLastMessages,
  fetchUsersSearch,
} from './models/api';
import useStore from '@/features/store';
import TopBar from './components/big/TopBar';
import { openDB } from '../indexdb';
import RecivedMessage from './components/small/RecivedMessage';
import ChatItem from './components/small/ChatItem';
import Group from './components/small/Group';
import GroupList from './components/medium/GroupList';
import RightPanel from './components/big/RightPanel';

export function LeftPanel() {
  const db = useStore((state) => state.indexDb);
  const isPersonalGroup = useStore((state) => state.isPersonalGroup);
  const mainWindow = useStore((state) => state.mainWindow);
  const leftCurrentPanel = useStore((state) => state.leftCurrentPanel);
  const setLeftCurrentPanel = useStore((state) => state.setLeftCurrentPanel);

  const [localIsPersonalGroup, setLocalIsPersonalGroup] = useState(isPersonalGroup);
  const [searchWord, setSearchWord] = useState();
  const [users, setUsers] = useState(null);

  useEffect(() => {
    if (!searchWord) {
      setUsers(null);
      return;
    }

    fetchUsersSearch(searchWord).then((data) => {
      setUsers(data);
    });
  }, [searchWord]);

  const onSubmit = (e) => {
    e.preventDefault();
    const formData = new FormData(e.target);
    fetch(`${process.env.NEXT_PUBLIC_API_PATH}/groups`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json', // Указываем JSON
      },
      body: JSON.stringify(Object.fromEntries(formData)),
      credentials: 'include',
    });
    // .then((response) => response.json())
    // .then((data) => {
    //   db.transaction('groups', 'readwrite').objectStore('groups').add(data);
    // });
  };
  return (
    <div className="top-lefter">
      <div className="left-panel-groups">
        {leftCurrentPanel != 'createGroup' && (
          <div className="search-bar">
            {mainWindow.innerWidth <= 1024 && <Burger />}
            <div className="zov">
              <IconSearch size={20} className="i" />
              <input
                type="text"
                placeholder=" Поиск"
                className="search-input"
                onChange={(e) => setSearchWord(e.target.value)}
              />
            </div>
          </div>
        )}

        {!users && leftCurrentPanel == 'main' ? (
          <div className="first_group">
            <div className="tabs">
              <button
                className={`tab ${localIsPersonalGroup && 'active'}`}
                onClick={() => setLocalIsPersonalGroup(true)}>
                Друзья
              </button>
              <button
                className={`tab ${!localIsPersonalGroup && 'active'}`}
                onClick={() => setLocalIsPersonalGroup(false)}>
                Группы
              </button>
            </div>
          </div>
        ) : (
          ''
        )}

        {leftCurrentPanel == 'createGroup' ? (
          <div className="create_group">
            <IconTransferOut onClick={() => setLeftCurrentPanel('main')} className="i" />
            <form onSubmit={onSubmit}>
              <label className="create_name">
                Название
                <input
                  className="create_name_input"
                  name="title"
                  type="text"
                  placeholder="Моя группа"
                  required
                />
              </label>
              <label className="create_desc">
                Краткое описание
                <textarea
                  className="create_desc_input"
                  name="description"
                  type="text"
                  placeholder="Группа разработчиков Margelet"
                  required
                />
              </label>
              <button type="submit" className="create_send">
                Создать
              </button>
            </form>
          </div>
        ) : (
          <div className="second_group">
            <div className="friends-list">
              <div className="friend-items">
                {searchWord ? (
                  <div className="search-users">
                    {users &&
                      users.map((item) => (
                        <div className="user-item" key={item.id}>
                          <div className="user_avatar_name">
                            <img className="user_avatar" />
                            <div className="item-name">{item.name}</div>
                          </div>
                          <div
                            className="users-add-friend"
                            onClick={() => {
                              fetch(
                                `${process.env.NEXT_PUBLIC_API_PATH}/users/add_friend/${item.id}`,
                                { method: 'POST', credentials: 'include' },
                              );
                            }}>
                            <div className="add-text">
                              <IconCodePlus stroke={2} className="i" />
                            </div>
                          </div>
                        </div>
                      ))}
                  </div>
                ) : (
                  <GroupList isPersonalGroup={localIsPersonalGroup} />
                )}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export function SentMessage({ text, created_at }) {
  return (
    <div className="message sent">
      <div className="message-content-u">
        <div className="message-author">Вы</div>
        <div className="message-text">{text}</div>
        <div className="message-time">{created_at}</div>
      </div>
    </div>
  );
}

export function Chat() {
  const myInputMessage = useRef(null);
  const messagesContainerRef = useRef(null);
  const groupId = useStore((state) => state.groupId);
  const chatId = useStore((state) => state.chatId);
  const ws = useStore((state) => state.ws);
  const db = useStore((state) => state.indexDb);
  const switchRerenderChat = useStore((state) => state.switchRerenderChat);
  const [messagesInChat, setMessagesInChat] = useState(null);
  // useEffect(() => {
  //   db.transaction('chatLastIdMessages', 'readwrite').objectStore('chatLastIdMessages').getAll().onsuccess = (event) => {
  //     setLastIdMessages(event.target.result);
  //   };
  // }, []);
  useEffect(() => {
    db
      .transaction('messages', 'readwrite')
      .objectStore('messages')
      .index('chat_id')
      .getAll(chatId).onsuccess = (event) => {
      setMessagesInChat(event.target.result);
    };
  }, [switchRerenderChat, chatId]);

  useEffect(() => {
    if (!groupId || !chatId) return;

    async function loadMessages() {
      const lastMessages = await fetchAllLastMessages([
        { group_id: groupId, chat_id: chatId, last_message_local_id: 0 },
      ]);
      const messages = [];

      if (!lastMessages) return;

      lastMessages.forEach((item) => {
        item.messages.forEach((message) => {
          db.transaction('messages', 'readwrite')
            .objectStore('messages')
            .add({
              messageId: message[0].id,
              authorId: message[1],
              name: message[2],
              ...message[0],
            });
          messages.push({
            messageId: message[0].id,
            authorId: message[1],
            name: message[2],
            ...message[0],
          });
        });
      });
      console.log(messages);
      setMessagesInChat(messages);
    }
    loadMessages();

    // db
    //   .transaction('messages', 'readwrite')
    //   .objectStore('messages')
    //   .index('chat_id')
    //   .getAll(chatId).onsuccess = (event) => {
    //     console.log(event.target.result);
    //     setMessagesInChat(event.target.result);
    //   };
  }, [chatId]);

  // useEffect(() => {
  //   if (!lastMessages) {
  //     return;
  //   }

  //   console.log(lastMessages);
  //   lastMessages.forEach((item) => {
  //     db.transaction('messages', 'readwrite').objectStore('messages').add({messageId: item.id, ...item});
  //   });
  // }, [isLoading]);

  useEffect(() => {
    //scroll to end chat when open
    if (messagesContainerRef.current) {
      messagesContainerRef.current.scrollTop = messagesContainerRef.current.scrollHeight;
    }
  }, [messagesContainerRef.current]);

  useEffect(() => {
    if (messagesContainerRef.current) {
      const scrollPosition = messagesContainerRef.current.scrollTop;
      const heightAll = messagesContainerRef.current.scrollHeight;
      const heightVisible = messagesContainerRef.current.offsetHeight;
      console.log(scrollPosition, heightAll, heightVisible);
      if (scrollPosition + heightVisible * 1.5 >= heightAll) {
        messagesContainerRef.current.scrollTop = heightAll;
      }
    }
  }, [messagesInChat]);

  const sendMessage = () => {
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(myInputMessage.current.value);
      myInputMessage.current.value = '';
    }
  };

  return (
    <div className="chat-area">
      {chatId ? (
        <>
          <div className="chat-messages" ref={messagesContainerRef}>
            {messagesInChat &&
              messagesInChat.map((item) => {
                return (
                  <RecivedMessage
                    key={item.messageId}
                    authorId={item.authorId}
                    text={item.text}
                    name={item.name}
                    createdAt={item.created_at}
                  />
                );
              })}
          </div>
          <div className="message-input-container">
            <div className="message-input">
              <div className="paperclip">
                <IconPaperclip stroke={2} className="i" />
              </div>
              <input
                ref={myInputMessage}
                type="text"
                placeholder="Enter the message"
                className="inputer"
                onKeyDown={(e) => {
                  if (e.key === 'Enter') {
                    sendMessage();
                  }
                }}
              />
            </div>
          </div>
        </>
      ) : (
        <div className="default">
          <div className="def-text">Выберите чат</div>
        </div>
      )}
    </div>
  );
}

export function GroupUsers() {
  return (
    <div className="right-panel-users" id="inactive">
      <div className="group_add_user">
        <div className="user-plus">
          <i className="bx bx-user-plus"></i>
        </div>
        <span className="adder">Добавить пользователя</span>
      </div>
      <div className="user-list">
        <span className="span">Участники</span>
        <div className="group-over">
          <div className="group-user-item">
            <img className="user-avatar"></img>
            <div className="user-info">
              <div className="user-name">Genesius Hrefler24</div>
              <div className="user-status">Онлайн</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export function Burger() {
  const setLeftCurrentPanel = useStore((state) => state.setLeftCurrentPanel);

  return (
    <DropdownMenu style={{ border: 'none' }}>
      <DropdownMenuTrigger>
        <IconMenu2 size={28} className="i" />
      </DropdownMenuTrigger>
      <DropdownMenuContent>
        <DropdownMenuItem>Настройки</DropdownMenuItem>
        <DropdownMenuItem onClick={() => setLeftCurrentPanel('createGroup')}>
          Создать группу
        </DropdownMenuItem>
        {/* <DropdownMenuItem>Team</DropdownMenuItem>
        <DropdownMenuItem>Subscription</DropdownMenuItem> */}
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
export function ControlPanel() {
  return (
    <>
      <div className="control-panel">
        <Burger />
        <button className="iconmenu2">
          <IconMessagePlus size={28} className="i" />
        </button>
      </div>
    </>
  );
}
export default function ChatPage() {
  // const user_part = [
  //   {id: 1, name: 'Валер Воро'},
  //   {id: 2, name: 'Валер Воро'},
  //   {id: 3, name: 'Валер Вороб'},
  //   {id: 4, name: 'Валер Воробeqgf'},
  // ]

  const chatId = useStore((state) => state.chatId);
  const groupId = useStore((state) => state.groupId);
  const db = useStore((state) => state.indexDb);
  const rerenderChat = useStore((state) => state.rerenderChat);
  const setWs = useStore((state) => state.setWs);
  const setIndexDb = useStore((state) => state.setIndexDb);
  const isPersonalGroup = useStore((state) => state.isPersonalGroup);

  const mainWindow = useStore((state) => state.mainWindow);
  const setMainWindow = useStore((state) => state.setMainWindow);
  const token = useTokenSWR().token;

  useEffect(() => {
    openDB()
      .then((db) => {
        setIndexDb(db);
      })
      .catch((error) => {});
  }, []);

  useEffect(() => {
    setMainWindow(window);
  });

  useEffect(() => {
    if (!chatId || !groupId || !db) {
      return;
    }
    const ws = new WebSocket(`${process.env.NEXT_PUBLIC_API_PATH}/chat/${chatId}?token=${token}`);
    ws.onopen = () => {
      console.log('Connected to chat:', chatId);
    };

    ws.onmessage = (event) => {
      const message = JSON.parse(event.data);
      db.transaction('messages', 'readwrite')
        .objectStore('messages')
        .add({
          messageId: message.message.id,
          authorId: message.author_id,
          name: message.author_name,
          ...message.message,
        });
      db.transaction('chatLastIdMessages', 'readwrite')
        .objectStore('chatLastIdMessages')
        .put({ chatId: chatId, localIdLastMessage: message.local_id });
      rerenderChat();
      console.log('Received message:', event.data);
    };

    ws.onclose = () => {
      console.log('Disconnected from chat:', chatId);
    };

    setWs(ws);

    return () => {
      if (ws) {
        ws.close();
      }
    };
  }, [chatId, groupId, db]);

  if (!mainWindow) return <></>;

  return (
    <div className="blocker">
      {mainWindow.innerWidth > 1024 && <ControlPanel />}
      {((mainWindow.innerWidth <= 768 && !groupId) || mainWindow.innerWidth > 768) && <LeftPanel />}
      {(mainWindow.innerWidth > 768 || groupId) && (
        <div className="rightblock">
          <TopBar />
          {groupId ? (
            <div className="chat-rightblock">
              {(mainWindow.innerWidth > 1024 || chatId) && <Chat />}
              {((mainWindow.innerWidth <= 1024 && !chatId) || mainWindow.innerWidth > 1024) && (
                <RightPanel />
              )}
            </div>
          ) : (
            <div className="default">
              <div className="def-text">Выберите группу</div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
