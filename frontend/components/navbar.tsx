"use client"
import { useState, useRef, useEffect } from "react"
import { useRouter } from "next/navigation"
import { SiOllama } from "react-icons/si"
import { RiNextjsFill } from "react-icons/ri"

export default function NavBar() {
  const router = useRouter()
  return (
    <>
      <div className="flex items-center w-full h-[80px] ml-0 justify-center md:ml-20 md:justify-start">
        <div className="flex flex-row justify-center text-center gap-3 items-center">
          <span
            className="text-white text-2xl font-bold opacity-60 hover:opacity-100 transition-opacity duration-300 ease-in-out cursor-pointer"
            onClick={() => router.push("/chat")}
          >
            Chat
          </span>
          <span
            className="text-white text-2xl font-bold opacity-60 hover:opacity-100 transition-opacity duration-300 ease-in-out cursor-pointer"
            onClick={() => router.push("/upload")}
          >
            Upload
          </span>
        </div>
      </div>
    </>
  )
}
