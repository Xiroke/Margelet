import useStore from '@/app/_store';
import './create_chat.css';
import BaseOverlay from '../base_overlay';
import { IconArrowLeft } from '@tabler/icons-react';

export default function CreateChat({ onClick }) {
    const db = useStore((state) => state.indexDb);
    const groupId = useStore((state) => state.groupId);
    const setRihtCurrentPanel = useStore((state) => state.setRightCurrentPanel);

  const onSubmit = (e) => {
    const formData = new FormData(e.target);
    e.preventDefault();
    fetch(`${process.env.NEXT_PUBLIC_API_PATH}/chat/chats/${groupId}?title=${formData.get('title')}`, {
      method: 'POST',
      credentials: 'include',
    }).then((response) => response.json())
    .then((newChat) => {
      // Обновляем IndexedDB
      const transaction = db.transaction("groups", "readwrite");
      const store = transaction.objectStore("groups");
      const request = store.get(groupId);

      request.onsuccess = (event) => {
        var groupData = event.target.result.groupData;
        groupData = groupData.chats.push(newChat); // Добавляем новый чат
        store.put({groupId: groupId, groupData: groupData}); // Сохраняем обновленные данные
      };
    })
  }

    return (
      <BaseOverlay onClick={onClick}>
        <div className='create-chat'>
            <div className="head">
              <button onClick={onClick} className='close-button'><IconArrowLeft stroke={2} className='i'/></button>
              <div className='create-chat_title'>Создание чата</div>
            </div>
            <form onSubmit={onSubmit} className='create-chat_form'>
              <label htmlFor='title'className='create-chat_label'>Название</label>
              <input
                id='title'
                name='title'
                type='text'
                placeholder='Моя группа'
                className='create-chat_input'
                required
              />
              <button type='submit' className='create-chat_btn'>Создать</button>
            </form>
            <div></div>
        </div>
      </BaseOverlay>
    )
}