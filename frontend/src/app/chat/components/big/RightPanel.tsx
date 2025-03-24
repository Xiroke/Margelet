import { useEffect, useState } from 'react';
import Image from 'next/image';

import useStore from '@/features/store';
import { getData } from '@/features/cacheStorage';
import CreateChat from '@/components/dialog/create_chat/create_chat';
import ChatList from '../medium/ChatList';

export default function RightPanel() {
  const isPersonalGroup = useStore((state) => state.isPersonalGroup);
  const groupId = useStore((state) => state.groupId);
  const db = useStore((state) => state.indexDb);
  const rightCurrentPanel = useStore((state) => state.rightCurrentPanel);
  const setChatId = useStore((state) => state.setChatId);
  const window = useStore((state) => state.mainWindow);

  const [groupName, setGroupName] = useState(null);
  const [isCreateChat, setIsCreateChat] = useState(false);
  const [panorama, setPanorama] = useState(null);

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

  useEffect(() => {
    if (!groupId) {
      return;
    }

    const loadPanorama = async () => {
      if (isPersonalGroup) {
        return;
      }
      //get Panorama photo from cacheStorage
      //"https://api.dicebear.com/6.x/initials/svg?seed=" + name
      const pathPhoto = await getData(
        `${process.env.NEXT_PUBLIC_API_PATH}/groups/group_panorama/${groupId}`,
        'photo',
        'group_panorama',
      );
      if (pathPhoto) {
        setPanorama(pathPhoto);
      }
    };

    loadPanorama();

    // return () => {
    //   URL.revokeObjectURL(panorama);
    // }
  }, [groupId]);

  if (isPersonalGroup) {
    return <></>;
  }

  if (rightCurrentPanel == 'main') {
    return (
      <>
        {isCreateChat && <CreateChat onClick={() => setIsCreateChat(false)} />}
        <div className="right-panel-chats">
          <div className="chat-avatar">
            <Image
              loader={({ src }) => `${src}`}
              className="avatar-img"
              onError={(e) => (e.target.style.display = 'none')}
              width="60"
              height="60"
              src={panorama ? panorama : '#'}
              alt="avatar"
              unoptimized={true}
            />
          </div>
          <div className="right-panel-chats-content">
            <div className="chat-header">{groupName}</div>
            <ChatList />
            {/* <div className='edit'>
                <button className='edit-btn'>
                  <IconEdit stroke={2} className='i' />
                </button>
              </div> */}
            <button className="right-panel_btn" onClick={() => setIsCreateChat(true)}>
              Создать чат
            </button>
          </div>
        </div>
      </>
    );
  } else if (rightCurrentPanel == 'users') {
    return <div className="right-panel-chats"></div>;
  }
}
