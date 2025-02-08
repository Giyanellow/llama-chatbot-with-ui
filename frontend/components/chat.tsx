"use client"
import { useState, useRef, useEffect } from "react"
import { ArrowUp, X } from "lucide-react"
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
import apiClient from "@/lib/api-client"
import ChatHeader from "./chat/chat-header"

const cookies = new Cookies()

export default function Chat() {
  const [input, setInput] = useState("")
  const [isReplying, setIsReplying] = useState(false)
  const [messages, setMessages] = useState<
    { content: string; role: string; id: number }[]
  >([])
  const [isMounted, setIsMounted] = useState(false)
  const [isDrawerOpen, setIsDrawerOpen] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

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

  const handlePromptClick = (message: string) => {
    setInput(message)
    handleSubmit(new Event("submit") as unknown as React.FormEvent)
  }

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
    animate: (i: number) => ({
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
    <div className="h-full bg-background text-foreground items-center justify-center w-full">
      <div className="max-w-2xl mx-auto w-full p-10 sm:px-0 md:p-0 flex flex-col flex-grow items-center justify-center h-full">
        {messages.length === 0 && <ChatHeader />}
        {/* Messages */}
        <div className="h-[350px] overflow-y-auto space-y-4 mb-4">
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
