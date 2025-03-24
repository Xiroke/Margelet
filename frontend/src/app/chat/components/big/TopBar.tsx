import Link from 'next/link';
import useStore from '@/features/store';
import { IconTransferOut, IconSettings, IconUsersGroup, IconHome } from '@tabler/icons-react';

export default function TopBar() {
  const window = useStore((state) => state.mainWindow);
  const setGroupId = useStore((state) => state.setGroupId);
  const setChatId = useStore((state) => state.setChatId);
  const setRightCurrentPanel = useStore((state) => state.setRightCurrentPanel);

  return (
    <div className="top-bar">
      {window.innerWidth <= 768 && (
        <div className="top-bar-content">
          <button className="top-bar-btn">
            <IconTransferOut
              onClick={() => {
                setGroupId(null);
                setChatId(null);
              }}
              stroke={2}
              className="i"
            />
          </button>
        </div>
      )}
      <div className="top-bar-content">
        <Link href="/chat/settings" className="top-bar-btn">
          <IconSettings stroke={2} className="i" />
        </Link>
        <button className="top-bar-btn" onClick={() => setRightCurrentPanel('users')}>
          <IconUsersGroup stroke={2} className="i" />
        </button>
        <button className="top-bar-btn" onClick={() => setRightCurrentPanel('main')}>
          <IconHome stroke={2} className="i" />
        </button>
      </div>
    </div>
  );
}
