"use client";

export function openDB() {
    return new Promise((resolve, reject) => {
        let openRequest = indexedDB.open("store", 1);

        openRequest.onupgradeneeded = function () {
            let db = openRequest.result;

            if (!db.objectStoreNames.contains("groups")) {
                db.createObjectStore("groups", { keyPath: "groupId" });
            }

            if (!db.objectStoreNames.contains("messages")) {
                const messagesStore = db.createObjectStore("messages", { keyPath: "messageId" });
                messagesStore.createIndex("chat_id", "chat_id");
            }

            if (!db.objectStoreNames.contains("chatLastIdMessages")) {
                db.createObjectStore("chatLastIdMessages", { keyPath: "chatId" });
            }

            if (!db.objectStoreNames.contains("avatarUrls")) {
                db.createObjectStore("avatarUrls", { keyPath: "userId" });
            }

        };

        openRequest.onerror = function () {
            reject(openRequest.error);
        };

        openRequest.onsuccess = function () {
            let db = openRequest.result;
            resolve(db);
        };
    })
}