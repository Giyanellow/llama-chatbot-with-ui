"use client"
import { useState, useRef, useEffect } from "react"
import { Paperclip, ArrowUp, X } from "lucide-react"
import { Button } from "@/components/ui/button"
import { SiOllama } from "react-icons/si"
import { RiNextjsFill } from "react-icons/ri"
import { cn } from "@/lib/utils"
import { ModeToggle } from "./mode-toggle"
import { Input } from "@/components/ui/input"
import axios from "axios"
import MarkdownRenderer from "./markdown-renderer"
import { motion } from "framer-motion"
import Cookies from "universal-cookie"

const cookies = new Cookies()

export default function Chat() {
  const [input, setInput] = useState("")
  const [isReplying, setIsReplying] = useState(false)
  const [messages, setMessages] = useState(() => {
    const savedMessages = localStorage.getItem("chatMessages")
    return savedMessages ? JSON.parse(savedMessages) : []
  })
  const messagesEndRef = useRef(null)
  const [isMounted, setIsMounted] = useState(false)
  const [sessionID, setSessionID] = useState("")

  const apiClient = axios.create({
    baseURL: process.env.NEXT_PUBLIC_BACKEND_URL,
    withCredentials: true, // Ensure cookies are included in requests
    headers: {
      "Content-Type": "application/json",
    },
  })

  const handleNewSession = async () => {
    try {
      const response = await apiClient.get("api/get_session_id")
      console.log(
        "Received new session ID from backend",
        response.data.session_id
      )
      // Set session_id cookie
      const sessionId = response.data.session_id
      if (sessionId) {
        cookies.set("session_id", sessionId, { path: "/" })
        setSessionID(sessionId)
        setMessages([])
      }
    } catch (error) {
      console.error("Error fetching new session ID:", error)
    }
  }

  const handleOldSession = async () => {
    try {
      const response = await apiClient.post("api/get_message_history", {
        session_id: cookies.get("session_id"),
      })
      console.log("Response of request", response)
      setMessages(response.data.messages)
    } catch (error) {
      console.error("Error fetching message history:", error)
    }
  }

  if (!isMounted) {
    if (!cookies.get("session_id")) {
      handleNewSession()
    } else {
      handleOldSession()
    }
    setIsMounted(true)
  }

  const examplePrompts = [
    {
      title: "Who are the characters",
      subtitle: "of the Harry Potter Books?",
    },
    {
      title: "What are the differences",
      subtitle: "of the Harry Potter books and movies?",
    },
    {
      title: "Who are the main characters",
      subtitle: "of the Harry Potter books?",
    },
    {
      title: "What happened",
      subtitle: "after the Harry Potter books?",
    },
  ]

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (input.trim()) {
      setMessages((prevMessages) => [
        ...prevMessages,
        { id: prevMessages.length, role: "user", content: input },
      ])
      setInput("")
      setIsReplying(true)

      try {
        const response = await apiClient.post("api/send_message", {
          message: input,
          session_id: cookies.get("session_id"),
        })

        setIsReplying(false)

        setMessages((prevMessages) => [
          ...prevMessages,
          {
            id: prevMessages.length,
            role: "assistant",
            content: response.data.message,
          },
        ])
      } catch (error) {
        console.error(error)
        setMessages((prevMessages) => [
          ...prevMessages,
          {
            id: prevMessages.length,
            role: "assistant",
            content: "I'm sorry, I don't understand that.",
          },
        ])
      }
    }
  }

  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: "smooth" })
    }
  }, [messages])

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setInput(e.target.value)
  }

  const dotVariants = {
    animate: (i) => ({
      opacity: [0, 1, 0],
      transition: {
        duration: 2,
        repeat: Infinity,
        ease: "easeInOut",
        delay: i * 0.3,
      },
    }),
  }

  const AnimatedDots = () => (
    <div className="flex p-4 rounded-lg w-fit space-x-2 bg-secondary text-secondary-foreground ml-3">
      {[...Array(3)].map((_, i) => (
        <motion.div
          key={i}
          className="w-2 h-2 bg-secondary-foreground rounded-full"
          variants={dotVariants}
          animate="animate"
          custom={i}
          style={{ animationDelay: `${i * 0.2}s` }}
        />
      ))}
    </div>
  )

  return (
    <div className="flex flex-col h-screen bg-background text-foreground p-4 md:p-8">
      <div className="max-w-2xl mx-auto max-h-screen w-full flex flex-col flex-grow">
        {messages.length === 0 && (
          <>
            {/* Header */}
            <div className="text-center mb-8">
              <div className="flex items-center justify-center gap-2 mb-6">
                <div className="text-3xl">
                  <SiOllama />
                </div>
                <div className="text-3xl">+</div>
                <div className="text-3xl">
                  <RiNextjsFill />
                </div>
              </div>
              <p className="text-muted-foreground mb-2">
                This is a{" "}
                <a href="#" className="underline hover:text-foreground">
                  sample chatbot
                </a>{" "}
                platform built with Next.js + shadcn and Ollama. It uses Python
                Flask as the backend and docker to containerize the entire
                platform
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
        )}
        {/* Messages */}
        <div className="flex-grow overflow-y-auto h-[100px] space-y-4 mb-4">
          {messages.map((message) => (
            <div
              key={message.id}
              className={cn(
                "flex p-4 rounded-lg w-fit max-w-[70%] whitespace-pre-wrap",
                message.role === "user"
                  ? "bg-primary text-primary-foreground ml-auto mr-3"
                  : "bg-secondary text-secondary-foreground ml-3"
              )}
            >
              <MarkdownRenderer content={message.content} />
            </div>
          ))}
          <div ref={messagesEndRef} />
          {isReplying && (
            <div className="flex p-4 rounded-lg w-fit">
              <AnimatedDots />
            </div>
          )}
        </div>

        {/* Example Prompts Grid */}
        {messages.length === 0 && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8">
            {examplePrompts.map((prompt, i) => (
              <button
                key={i}
                className="p-4 text-left rounded-2xl border border-border hover:bg-accent hover:text-accent-foreground transition-colors"
                onClick={() =>
                  handlePromptClick(`${prompt.title} ${prompt.subtitle}`)
                }
              >
                <div className="text-foreground">{prompt.title}</div>
                <div className="text-muted-foreground">{prompt.subtitle}</div>
              </button>
            ))}
          </div>
        )}

        {/* Input Form */}
        <div className="flex flex-row gap-3 items-center flex-shrink-0">
          <form
            onSubmit={handleSubmit}
            className="relative flex flex-row w-full items-center"
          >
            <Input
              value={input}
              onChange={handleInputChange}
              placeholder="Send a message..."
              className="w-full h-11 pr-24"
            />
            <div className="absolute right-2 top-1/2 -translate-y-1/2 flex items-center gap-2">
              <Button
                type="submit"
                size="icon"
                className="bg-primary h-7 w-7 text-primary-foreground hover:bg-primary/90"
                disabled={!input}
              >
                <ArrowUp className="h-4 w-4" />
              </Button>
            </div>
          </form>
          <ModeToggle />
          <Button
          type="button"
          size="icon"
          variant="outline"
          className="bg-primary-foreground text-primary hover:bg-secondary/90"
          onClick={handleNewSession}
          >
            <X className="h-[1.2rem] w-[1.2rem]" />
          </Button>
        </div>
      </div>
    </div>
  )
}
