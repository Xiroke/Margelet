"use client";

export async function getChats(group_id) {
    try {
        const res = await fetch(`http://localhost:8000/api/chat/get_group_chats?group_id=${group_id}`, {
            method: "GET",
            credentials: "include"
        });
        return res.json();
    } catch (error) {
        console.log(error);
    }
}

export async function getGroups() {
    try {
        const res = await fetch(`http://localhost:8000/api/chat/get_my_groups`, {
            method: "GET",
            credentials: "include"
        });
        return res.json();
    } catch (error) {
        console.log(error);
    }
    
}

