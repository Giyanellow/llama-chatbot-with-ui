"use client"
import { SiOllama } from 'react-icons/si';
import { RiNextjsFill } from 'react-icons/ri';


export default function ChatHeader() {
  return (
    <>
      {/* Header */}
      <div className="text-center mb-8">
        <div className="flex items-center justify-center gap-2 mb-6 text-3xl">
          <div>
            <SiOllama />
          </div>
          <div>+</div>
          <div>
            <RiNextjsFill />
          </div>
        </div>
        <p className="text-muted-foreground mb-2">
          This is a{" "}
          <a href="#" className="underline hover:text-foreground">
            sample chatbot
          </a>{" "}
          platform built with Next.js + shadcn and Ollama. It uses Python Flask
          as the backend and docker to containerize the entire platform
        </p>
        <p className="text-muted-foreground">
          You can check out my other projects by visiting my{" "}
          <a
            href="https://github.com/Giyanellow"
            className="underline hover:text-foreground"
          >
            github
          </a>
          .
        </p>
      </div>
    </>
  )
}
