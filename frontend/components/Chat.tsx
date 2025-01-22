"use client"

import { useState } from "react"
import { Paperclip, ArrowUp } from 'lucide-react'
import { Button } from "@/components/ui/button"
import { SiOllama } from "react-icons/si"
import { RiNextjsFill } from "react-icons/ri"
import { cn } from "@/lib/utils"
import { ModeToggle } from "./ModeToggle"
import { Input } from "@/components/ui/input"

export default function Chat() {
  const [input, setInput] = useState("")
  const [messages, setMessages] = useState([])

  const examplePrompts = [
    {
      title: "What are the advantages",
      subtitle: "of using Next.js?",
    },
    {
      title: "Write code to",
      subtitle: "demonstrate dijkstra's algorithm",
    },
    {
      title: "Help me write an essay",
      subtitle: "about silicon valley",
    },
    {
      title: "What is the weather",
      subtitle: "in San Francisco?",
    },
  ]

  const handlePromptClick = (prompt: string) => {
    setInput(prompt)
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (input.trim()) {
      setMessages((prevMessages) => [
        ...prevMessages,
        { id: prevMessages.length, role: "user", content: input },
      ])
      setInput("")
    }
  }

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setInput(e.target.value)
  }

  return (
    <div className="flex flex-col min-h-screen bg-background text-foreground p-4 md:p-8">
      <div className="max-w-2xl mx-auto w-full flex flex-col flex-grow">
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
            Flask as the backend and docker to containerize the entire platform
          </p>
          <p className="text-muted-foreground">
            You can check out my other projects by visiting my{" "}
            <a href="https://github.com/Giyanellow" className="underline hover:text-foreground">
              github
            </a>
            .
          </p>
        </div>

        {/* Messages */}
        <div className="flex-grow space-y-4 mb-4">
          {messages.map((message) => (
            <div
              key={message.id}
              className={cn(
                "p-4 rounded-lg",
                message.role === "user"
                  ? "bg-primary text-primary-foreground ml-auto max-w-[50%]"
                  : "bg-secondary text-secondary-foreground"
              )}
            >
              {message.content}
            </div>
          ))}
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
        <form
          onSubmit={handleSubmit}
          className="relative flex flex-row items-center"
        >
          <Input
            value={input}
            onChange={handleInputChange}
            placeholder="Send a message..."
            className="w-full pr-24"
          />
          <div className="absolute right-2 top-1/2 -translate-y-1/2 flex items-center gap-2">
            <Button
              type="button"
              variant="ghost"
              size="icon"
              className="text-muted-foreground hover:text-foreground"
            >
              <Paperclip className="h-5 w-5" />
            </Button>
            <Button
              type="submit"
              size="icon"
              className="bg-primary text-primary-foreground hover:bg-primary/90"
              disabled={!input}
            >
              <ArrowUp className="h-4 w-4" />
            </Button>
            <ModeToggle />
          </div>
        </form>
      </div>
    </div>
  )
}