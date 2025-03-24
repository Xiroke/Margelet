import { getData } from '@/features/cacheStorage.ts';
import Image from 'next/image';
import path from 'path';
import { useState, useEffect } from 'react';

export default function RecivedMessage({ authorId, text, createdAt, name }) {
  const [avatar, setAvatar] = useState<string>('');

  useEffect(() => {
    if (!authorId) {
      return;
    }

    const loadAvatar = async () => {
      //get avatar photo from cacheStorage
      //"https://api.dicebear.com/6.x/initials/svg?seed=" + name
      const pathAvatar = await getData(
        `${process.env.NEXT_PUBLIC_API_PATH}/users/avatar?user_id=${authorId}`,
        'photo',
        'user_avatar',
      );
      if (pathAvatar) {
        setAvatar(pathAvatar);
      } else {
        setAvatar('https://api.dicebear.com/6.x/initials/svg?seed=' + name);
      }
    };

    loadAvatar();

    // return () => {
    //     URL.revokeObjectURL(avatar);
    // }
  }, [authorId]);

  if (!authorId || !name || !createdAt || !text) {
    return;
  }

  return (
    <div className="message received">
      <div className="message_avatar_container">
        {avatar && (
          <Image
            loader={({ src }) => `${src}`}
            className="message_avatar"
            width="60"
            height="60"
            src={avatar}
            alt="avatar"
            unoptimized={true}
          />
        )}
      </div>
      <div className="message-content">
        <div className="message-author">{name}</div>
        <div className="message-text-data">
          <div className="message-text">{text}</div>
          <div className="message-time">
            {new Date(createdAt).toLocaleString([], {
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
