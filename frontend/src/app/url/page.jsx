"use client"
import {useEffect} from "react";
import "./logstyle.css"

export default function Test() {
  return (
    <>
      <div className="flex flex-col relative">
          <div className="bg-red-800 w-40 h-40"></div>
          <div className="bg-red-800 w-40 h-40"></div>
          <div className="bg-red-800 w-40 h-40"></div>
          <div className="bg-red-800 w-40 h-40"></div>
          <div className="absolute bottom-0 top-auto block w-full h-40"></div>
      </div>
    </>
  );
}
