import { create } from 'zustand';


const useStore = create((set) => ({
  groupId: null,
  chatId: null,
  myInputMessage: null,
  ws: null,
  indexDb: null,
  switchRerenderChat: null,
  isPersonalGroup: false,
  leftCurrentPanel: 'main', //main or createGroup
  rightCurrentPanel: 'main', //main or users
  mainWindow: null,

  rerenderChat: () =>
    set(() => ({
      switchRerenderChat: Math.random(),
    })),
  setMainWindow: (window) =>
    set(() => ({
      mainWindow: window,
    })),
  setGroupId: (groupId) =>
    set(() => ({
      groupId: groupId,
    })),
  setChatId: (chatId) =>
    set(() => ({
      chatId: chatId,
    })),
  setMyInputMessage: (message) =>
    set(() => ({
      myInputMessage: message,
    })),
  setWs: (ws) =>
    set(() => ({
      ws: ws,
    })),
  setIndexDb: (indexDb) =>
    set(() => ({
      indexDb: indexDb,
    })),
  setIsPersonalGroup: (isPersonalGroup) =>
    set(() => ({
      isPersonalGroup: isPersonalGroup,
    })),
  setRightCurrentPanel: (rightCurrentPanel) =>
    set(() => ({
      rightCurrentPanel: rightCurrentPanel,
    })),
  setLeftCurrentPanel: (leftCurrentPanel) =>
    set(() => ({
      leftCurrentPanel: leftCurrentPanel,
    })),
}));

export default useStore;
