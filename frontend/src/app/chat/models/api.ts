'use client';

import useSWR from 'swr';
import 'dotenv/config';

const fetcherGet = (url) =>
  fetch(url, { credentials: 'include' }).then((res) => (res.status == 200 ? res.json() : null));
const fetcherPost = (url) =>
  fetch(url, { credentials: 'include', method: 'POST' }).then((res) =>
    res.status == 200 ? res.json() : null,
  );

export function useGroupsSWR() {
  const { data, error, isLoading } = useSWR(
    `${process.env.NEXT_PUBLIC_API_PATH}/groups/me`,
    fetcherGet,
  );

  return {
    groups: data,
    error,
    isLoading,
  };
}

export function useChatsSWR(group_id) {
  const { data, error, isLoading } = useSWR(
    `${process.env.NEXT_PUBLIC_API_PATH}/chats/${group_id}`,
    fetcherGet,
  );

  return {
    chats: data,
    error,
    isLoading,
  };
}

export function useLastMessageSWR(group_id, chat_id, last_message_local_id) {
  const { data, error, isLoading } = useSWR(
    `${process.env.NEXT_PUBLIC_API_PATH}/chat/chat_last_messages/${group_id}/${chat_id}?last_message_local_id=${last_message_local_id}`,
    fetcherGet,
  );

  return {
    last_message: data,
    error,
    isLoading,
  };
}

export function useTokenSWR() {
  const { data, error, isLoading } = useSWR(
    `${process.env.NEXT_PUBLIC_API_PATH}/auth/get_token`,
    fetcherGet,
  );

  return {
    token: data,
    error,
    isLoading,
  };
}

export function useSearchUsersSWR() {
  const { data, error, isLoading } = useSWR(
    `${process.env.NEXT_PUBLIC_API_PATH}/users/search`,
    fetcherGet,
  );

  return {
    users: data,
    error,
    isLoading,
  };
}

export function useUsersMeSWR() {
  const { data, error, isLoading } = useSWR(
    `${process.env.NEXT_PUBLIC_API_PATH}/auth/users/me`,
    fetcherGet,
  );

  return {
    user: data,
    error,
    isLoading,
  };
}

export function fetchAllLastMessages(params) {
  return fetch(
    `${process.env.NEXT_PUBLIC_API_PATH}/chat/chat_all_last_messages?params=${JSON.stringify(
      params,
    )}`,
    {
      method: 'GET',
      credentials: 'include',
    },
  ).then((response) => {
    if (response.status == 200) return response.json();
    return null;
  });
}

export function fetchAvatar(id, name_account) {
  if (id) return fetcherGet(`${process.env.NEXT_PUBLIC_API_PATH}/users/avatar?user_id=${id}`);
  else if (name_account)
    return fetchGet(
      `${process.env.NEXT_PUBLIC_API_PATH}/users/avatar?user_name_account=${name_account}`,
    );
  else return null;
}

export const fetchUsersSearch = (searchWord) =>
  fetcherGet(`${process.env.NEXT_PUBLIC_API_PATH}/users/search/${searchWord}`);
