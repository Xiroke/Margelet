import { useEffect } from 'react';
import Group from '../small/Group';
import { useGroupsSWR } from '../../models/api';
import useStore from '@/features/store';

export default function GroupList({ isPersonalGroup }) {
  const { groups, error, isLoading } = useGroupsSWR();
  const db = useStore((state) => state.indexDb);

  useEffect(() => {
    const initDB = async () => {
      if (isLoading || !db) {
        return;
      }

      try {
        const transaction = db.transaction('groups', 'readwrite').objectStore('groups');
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
    <div className="friend-groups-lst">
      <div className="friend-group">
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
                ),
            )
          : 'Нет групп'}
      </div>
    </div>
  );
}
