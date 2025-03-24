type DataType = 'photo' | 'json';
type DataTitle = 'user_avatar' | 'group_panorama';

export async function getData(url: string, type: DataType, title: DataTitle) {
  const cacheVersion = 1;
  const cacheName = `my_app-${title}-${cacheVersion}`;
  let cachedData = await getCachedData(cacheName, url, type, title);

  //if data in cache we return it
  if (cachedData) {
    return cachedData;
  }

  let response = await fetch(url, { credentials: 'include' });

  let data;
  let newResponse;
  if (response.ok) {
    if (type === 'photo') {
      data = await response.blob();
      newResponse = new Response(data, {
        headers: { 'Content-Type': 'image/jpeg' },
      });
    } else if ((type = 'json')) {
      data = await response.json();
      newResponse = new Response(data, {
        headers: { 'Content-Type': 'application/json' },
      });
    }
  } else {
    newResponse = new Response(null, { status: response.status });
  }
  // Сохраняем ответ в кэше с правильным Content-Type
  const cacheStorage = await caches.open(cacheName);

  if (!newResponse) {
    return undefined;
  }

  await cacheStorage.put(url, newResponse);

  // Удаляем старые кэши
  await deleteOldCaches(cacheName);

  return data;
}

export async function getCachedData(
  cacheName: string,
  url: string,
  type: DataType,
  title: DataTitle,
) {
  const cacheStorage = await caches.open(cacheName);
  const cachedResponse = await cacheStorage.match(url);

  if (!cachedResponse || !cachedResponse.ok) {
    return false;
  }

  if (type === 'photo') {
    // const image = await db.images.get(id);
    // if (image) {
    //   return image.path;
    // } else {
    //   const urlBlob = URL.createObjectURL(await cachedResponse.blob());
    //   await db.images.add({ id: id, title: title, path: urlBlob });
    //   return urlBlob;
    // }
    return URL.createObjectURL(await cachedResponse.blob());
  }

  return await cachedResponse.json();
}

// Delete any old caches to respect user's disk space.
export async function deleteOldCaches(currentCache: string) {
  const keys = await caches.keys();

  for (const key of keys) {
    const isOurCache = key.startsWith('myapp-');
    if (currentCache === key || !isOurCache) {
      continue;
    }
    caches.delete(key);
  }
}
