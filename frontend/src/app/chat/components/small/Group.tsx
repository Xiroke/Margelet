import useStore from '@/features/store';
import { useUsersMeSWR } from '../../models/api';

export default function Group({ id, title, status, isPersonalGroup }) {
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
      className="friend-item"
      onClick={() => {
        setGroupId(id);
        !isPersonalGroup && setChatId(null); //fix behavior when click on group after personal group
        setIsPersonalGroup(isPersonalGroup);
      }}>
      <div className="group_avatar_container">
        <img className="group_avatar" onError={(e) => (e.target.style.display = 'none')} />
        <span className="group_avatar_placeholder">{title.slice(0, 2)}</span>
      </div>
      <div className="friend-info">
        <div className="friend-name">{title}</div>
        {!isPersonalGroup && <div className="friend-status">{status}</div>}
      </div>
    </div>
  );
}
