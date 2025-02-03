'use client';
import React, { use, useEffect, useRef, useState } from 'react';
import {
  useChatsSWR,
  useGroupsSWR,
  useTokenSWR,
  useUsersMeSWR,
  fetchAllLastMessages,
} from './_api';
import useStore from '../_store';
import { openDB } from '../_indexdb';
import CreateChat from '@/components/dialog/create_chat/create_chat';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import {
  IconSearch,
  IconPaperclip,
  IconEdit,
  IconSettings,
  IconHome,
  IconUsersGroup,
  IconMenu2,
  IconMessagePlus,
  IconCodePlus,
  IconTransferOut,
} from '@tabler/icons-react';
import { Image } from 'next/image';
import Link from 'next/link';
import ReactCrop from 'react-image-crop';
import 'react-image-crop/dist/ReactCrop.css';
import './styles.css';

export function TopBar() {
  const window = useStore((state) => state.mainWindow);
  const setGroupId = useStore((state) => state.setGroupId);
  const setChatId = useStore((state) => state.setChatId);
  const setRightCurrentPanel = useStore((state) => state.setRightCurrentPanel);

  return (
    <div className='top-bar'>
      {window.innerWidth <= 768 && (
        <div className='top-bar-content'>
          <button className='top-bar-btn'>
            <IconTransferOut
              onClick={() => {
                setGroupId(null);
                setChatId(null);
              }}
              stroke={2}
              className='i'
            />
          </button>
        </div>
      )}
      <div className='top-bar-content'>
        <Link href="/chat/settings" className='top-bar-btn'>
          <IconSettings stroke={2} className='i' />
        </Link>
        <button
          className='top-bar-btn'
          onClick={() => setRightCurrentPanel('users')}
        >
          <IconUsersGroup stroke={2} className='i' />
        </button>
        <button
          className='top-bar-btn'
          onClick={() => setRightCurrentPanel('main')}
        >
          <IconHome stroke={2} className='i' />
        </button>
      </div>
    </div>
  );
}

export function Group({ id, title, status, isPersonalGroup }) {
  const setGroupId = useStore((state) => state.setGroupId);
  const setChatId = useStore((state) => state.setChatId);
  const setIsPersonalGroup = useStore((state) => state.setIsPersonalGroup);
  const { user } = useUsersMeSWR();
  title = isPersonalGroup
    ? title
        .split(':')[0]
        .split('|')
        .filter((i) => i != user.name_account)[0]
    : title;

  return (
    <div
      className='friend-item'
      onClick={() => {
        setGroupId(id);
        !isPersonalGroup && setChatId(null); //fix behavior when click on group after personal group
        setIsPersonalGroup(isPersonalGroup);
      }}
    >
      <div className='group_avatar_container'>
        <img
          className='group_avatar'
          onError={(e) => (e.target.style.display = 'none')}
        />
        <span className='group_avatar_placeholder'>{title.slice(0, 2)}</span>
      </div>
      <div className='friend-info'>
        <div className='friend-name'>{title}</div>
        {!isPersonalGroup && <div className='friend-status'>{status}</div>}
      </div>
    </div>
  );
}

export function GroupList({ isPersonalGroup }) {
  const { groups, error, isLoading } = useGroupsSWR();
  const db = useStore((state) => state.indexDb);

  useEffect(() => {
    const initDB = async () => {
      if (isLoading || !db) {
        return;
      }

      try {
        const transaction = db
          .transaction('groups', 'readwrite')
          .objectStore('groups');
        const transaction2 = db
          .transaction('chatLastIdMessages', 'readwrite')
          .objectStore('chatLastIdMessages');
        groups.forEach((group) => {
          transaction.put({ groupId: group.id, groupData: group });
          group.chats.forEach((chat) => {
            const chatIdRequest = transaction2.get(chat.id);
            chatIdRequest.onsuccess = (event) => {
              const chatId = event.target.result;
              if (!chatId) {
                transaction2.add({ chatId: chat.id, localIdLastMessage: 0 });
              }
            };
          });
        });
      } catch (error) {
        console.log(error);
      }
    };
    initDB();
  }, [isLoading, db]);
  return (
    <div className='friend-groups-lst'>
      <div className='friend-group'>
        {groups
          ? groups.map(
              (item) =>
                item.is_personal_group == isPersonalGroup && (
                  <Group
                    id={item.id}
                    key={item.id}
                    title={item.title}
                    status={item.description}
                    isPersonalGroup={isPersonalGroup}
                  />
                )
            )
          : 'Нет групп'}
      </div>
    </div>
  );
}

export function LeftPanel() {
  const db = useStore((state) => state.indexDb);
  const isPersonalGroup = useStore((state) => state.isPersonalGroup);
  const mainWindow = useStore((state) => state.mainWindow);
  const leftCurrentPanel = useStore((state) => state.leftCurrentPanel);
  const setLeftCurrentPanel = useStore((state) => state.setLeftCurrentPanel)

  const [localIsPersonalGroup, setLocalIsPersonalGroup] =
    useState(isPersonalGroup);
  const [searchWord, setSearchWord] = useState();
  const [users, setUsers] = useState(null);

  useEffect(() => {
    if (!searchWord) {
      setUsers(null);
      return;
    }
    fetch(`${process.env.NEXT_PUBLIC_API_PATH}/chat/users/${searchWord}`, {
      credentials: 'include',
    })
      .then((response) => (response.status == 200 ? response.json() : null))
      .then((data) => {
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
    <div className='top-lefter'>
      <div className='left-panel-groups'>
        
        {leftCurrentPanel != 'createGroup' && <div className='search-bar'>
          {mainWindow.innerWidth <= 1024 && <Burger />}
          <div className='zov'>
            <IconSearch size={20} className='i' />
            <input
              type='text'
              placeholder=' Поиск'
              className='search-input'
              onChange={(e) => setSearchWord(e.target.value)}
            />
          </div>
        </div>}

        {!users && leftCurrentPanel == 'main' ? (
          <div className='first_group'>
            <div className='tabs'>
              <button
                className={`tab ${localIsPersonalGroup && 'active'}`}
                onClick={() => setLocalIsPersonalGroup(true)}
              >
                Друзья
              </button>
              <button
                className={`tab ${!localIsPersonalGroup && 'active'}`}
                onClick={() => setLocalIsPersonalGroup(false)}
              >
                Группы
              </button>
            </div>
          </div>
        ) : (
          ''
        )}

        {leftCurrentPanel == 'createGroup' ? (
          <div className='create_group'>
            <IconTransferOut onClick={() => setLeftCurrentPanel('main')} className='i' />
            <form onSubmit={onSubmit}>
            <label className="create_name">
                Название
                <input className="create_name_input"
                  name='title'
                  type='text'
                  placeholder='Моя группа'
                  required
                />
              </label>
              <label className="create_desc">
                Краткое описание
                <textarea className="create_desc_input"
                  name='description'
                  type='text'
                  placeholder='Группа разработчиков Margelet'
                  required
                />
              </label>
              <button type='submit' className="create_send">Создать</button>
            </form>
          </div>
        ) : (
          <div className='second_group'>
            <div className='friends-list'>
              <div className='friend-items'>
                {searchWord ? (
                  <div className='search-users'>
                    {users &&
                      users.map((item) => (
                        <div className='user-item' key={item.id}>
                          <div className='user_avatar_name'>
                            <img
                              className='user_avatar'
                            />
                            <div className='item-name'>{item.name}</div>
                          </div>
                          <div
                            className='users-add-friend'
                            onClick={() => {
                              fetch(
                                `${process.env.NEXT_PUBLIC_API_PATH}/chat/users/add_friend/${item.id}`,
                                { method: 'POST', credentials: 'include' }
                              );
                            }}
                          >
                            <div className='add-text'>
                              <IconCodePlus stroke={2} className='i' />
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

export function RecivedMessage({ text, created_at, name }) {
  if (!name || !created_at || !text) {
    return;
  }
  return (
    <div className='message received'>
      <div className='message_avatar_container'>
        <img
          className='message_avatar'
          onError={(e) => (e.target.style.display = 'none')}
        />
        <span className='message_avatar_placeholder'>{name.slice(0, 2)}</span>
      </div>
      <div className='message-content'>
        <div className='message-author'>{name}</div>
        <div className='message-text-data'>
          <div className='message-text'>{text}</div>
          <div className='message-time'>
            {new Date(created_at.replace(' ', 'T') + 'Z').toLocaleString([], {
              hour: '2-digit',
              minute: '2-digit',
              hour12: false,
            })}
          </div>
        </div>
      </div>
    </div>
  );
}

export function SentMessage({ text, created_at }) {
  return (
    <div className='message sent'>
      <div className='message-content-u'>
        <div className='message-author'>Вы</div>
        <div className='message-text'>{text}</div>
        <div className='message-time'>{created_at}</div>
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
      const lastMessages = await fetchAllLastMessages([{ group_id: groupId, chat_id: chatId, last_message_local_id: 0 }]);
      const messages = []

      if (!lastMessages) return;

      lastMessages.forEach((item) => {
        item.messages.forEach((message) => {
          db.transaction('messages', 'readwrite')
            .objectStore('messages')
            .add({ messageId: message[0].id, name: message[1], ...message[0]});
            messages.push({ messageId: message[0].id, name: message[1], ...message[0]});
        });
      });

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
      messagesContainerRef.current.scrollTop =
        messagesContainerRef.current.scrollHeight;
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
    <div className='chat-area'>
      {chatId ? (
        <>
          <div className='chat-messages' ref={messagesContainerRef}>
            {messagesInChat &&
              messagesInChat.map((item, index) => {
                return (
                  <RecivedMessage
                    key={index}
                    text={item.text}
                    name={item.name}
                    created_at={item.created_at}
                  />
                );
              })}
          </div>
          <div className='message-input-container'>
            <div className='message-input'>
              <div className='paperclip'>
                <IconPaperclip stroke={2} className='i' />
              </div>
              <input
                ref={myInputMessage}
                type='text'
                placeholder='Enter the message'
                className='inputer'
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
        <div className='default'>
          <div className='def-text'>Выберите чат</div>
        </div>
      )}
    </div>
  );
}

export function ChatItem({ id, title, type, isActive }) {
  const setChatId = useStore((state) => state.setChatId);

  return (
    <div
      className={`chat-action-btn ${isActive && 'chat-action-btn-active'}`}
      onClick={() => setChatId(id)}
    >
      <div className='bx'>
        <i className='bx bx-hash'></i>
      </div>
      <div className='bx2'>
        <span className='base-chanel-name'>{title}</span>
      </div>
    </div>
  );

  // <div className='voice-channel'>
  //   <div className='mic'>
  //     <i className='bx bxs-microphone'></i>
  //     <span className='chanel-name'> Основной</span>
  //   </div>
  //   <div className='mic'>
  //     <i className='bx bxs-user'></i>
  //     <span className='member-count'> 4</span>
  //   </div>
  // </div>
}

export function ChatsList() {
  const groupId = useStore((state) => state.groupId);
  const { chats, error, isLoading } = useChatsSWR(groupId);
  const chatId = useStore((state) => state.chatId);

  useEffect(() => {
    //rerender for active chat
  }, [chatId]);

  return (
    <div className='chat-actions'>
      <h3>Чаты</h3>
      {chats
        ? chats.map((item) => (
            <ChatItem
              key={item.id}
              id={item.id}
              title={item.title}
              type={item.type}
              isActive={item.id === chatId}
            />
          ))
        : 'Загрузка...'}
    </div>
  );
}

export function GroupUsers() {
  return (
    <div className='right-panel-users' id='inactive'>
      <div className='group_add_user'>
        <div className='user-plus'>
          <i className='bx bx-user-plus'></i>
        </div>
        <span className='adder'>Добавить пользователя</span>
      </div>
      <div className='user-list'>
        <span className='span'>Участники</span>
        <div className='group-over'>
          <div className='group-user-item'>
            <img className='user-avatar'></img>
            <div className='user-info'>
              <div className='user-name'>Genesius Hrefler24</div>
              <div className='user-status'>Онлайн</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export function RightPanel() {
  const isPersonalGroup = useStore((state) => state.isPersonalGroup);
  const groupId = useStore((state) => state.groupId);
  const db = useStore((state) => state.indexDb);
  const rightCurrentPanel = useStore((state) => state.rightCurrentPanel);
  const setChatId = useStore((state) => state.setChatId);

  const [groupName, setGroupName] = useState(null);
  const [isCreateChat, setIsCreateChat] = useState(false);

  useEffect(() => {
    const group = db.transaction('groups', 'readwrite').objectStore('groups');
    const groupResult = group.get(groupId);

    groupResult.onsuccess = (event) => {
      setGroupName(event.target.result.groupData.title);
    };

    if (isPersonalGroup) {
      groupResult.onsuccess = (event) => {
        setChatId(event.target.result.groupData.chats[0].id);
      };
    }
  }, [groupId]);

  if (isPersonalGroup) {
    return <></>;
  }

  if (rightCurrentPanel == 'main') {
    return (
      <>
        {isCreateChat && <CreateChat onClick={() => setIsCreateChat(false)}/>}
        <div className='right-panel-chats'>
          <div className='chat-avatar'>
            <img  className='avatar-img'></img>
          </div>
          <div className='right-panel-chats-content'>
            <div className='chat-header'>{groupName}</div>
            <ChatsList />
            {/* <div className='edit'>
              <button className='edit-btn'>
                <IconEdit stroke={2} className='i' />
              </button>
            </div> */}
            <button className="right-panel_btn" onClick={() => setIsCreateChat(true)}>Создать чат</button>
          </div>
        </div>
        </>
    );
  } else if (rightCurrentPanel == 'users') {
    return <div className='right-panel-chats'></div>;
  }
}

export function Burger() {
  const setLeftCurrentPanel = useStore((state) => state.setLeftCurrentPanel);

  return (
    <DropdownMenu style={{ border: 'none' }}>
      <DropdownMenuTrigger>
        <IconMenu2 size={28} className='i' />
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
      <div className='control-panel'>
        <Burger />
        <button className='iconmenu2'>
          <IconMessagePlus size={28} className='i' />
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
    let ws;
    ws = new WebSocket(
      `${process.env.NEXT_PUBLIC_API_PATH}/chat/${chatId}?token=${token}`
    );
    ws.onopen = () => {
      console.log('Connected to chat:', chatId);
    };

    ws.onmessage = (event) => {
      const message = JSON.parse(event.data);
      rerenderChat();
      db.transaction('messages', 'readwrite')
        .objectStore('messages')
        .add({ messageId: message.id, ...message });
      db.transaction('chatLastIdMessages', 'readwrite')
        .objectStore('chatLastIdMessages')
        .put({ chatId: chatId, localIdLastMessage: message.local_id });
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
    <div className='blocker'>
      {mainWindow.innerWidth > 1024 && <ControlPanel />}
      {((mainWindow.innerWidth <= 768 && !groupId) ||
        mainWindow.innerWidth > 768) && <LeftPanel />}
      {(mainWindow.innerWidth > 768 || groupId) && (
        <div className='rightblock'>
          <TopBar />
          {groupId ? (
            <div className='chat-rightblock'>
              {(mainWindow.innerWidth > 1024 || chatId) && <Chat />}
              {((mainWindow.innerWidth <= 1024 && !chatId) ||
                mainWindow.innerWidth > 1024) && <RightPanel />}
            </div>
          ) : (
            <div className='default'>
              <div className='def-text'>Выберите группу</div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
