import useStore from '@/features/store';

export default function ChatItem({ id, title, type, isActive }) {
  const setChatId = useStore((state) => state.setChatId);

  return (
    <div
      className={`chat-action-btn ${isActive && 'chat-action-btn-active'}`}
      onClick={() => setChatId(id)}>
      <div className="bx">
        <i className="bx bx-hash"></i>
      </div>
      <div className="bx2">
        <span className="base-chanel-name">{title}</span>
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
