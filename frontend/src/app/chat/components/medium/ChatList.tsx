import useStore from '@/features/store';
import { useEffect } from 'react';
import { useChatsSWR } from '../../models/api';
import ChatItem from '../small/ChatItem';

export default function ChatList() {
  const groupId = useStore((state) => state.groupId);
  const { chats, error, isLoading } = useChatsSWR(groupId);
  const chatId = useStore((state) => state.chatId);

  useEffect(() => {
    //rerender for active chat
  }, [chatId]);

  return (
    <div className="chat-actions">
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
