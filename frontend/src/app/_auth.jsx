"use server";
import { cookies } from "next/headers";
import { redirect } from "next/navigation";

export async function isAuthenticated() {
    const token = cookies().get("access_token");
    if (token) {
        return true;
    } else {
        redirect("/");
    }
}


export async function isLogined() {
    const token = cookies().get("access_token");
    if (token) {
        redirect("/chat");;
    } else {
        return false
    }
}
