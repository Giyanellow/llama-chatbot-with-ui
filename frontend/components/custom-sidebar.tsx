"use client"

import type React from "react"
import { useState } from "react"
import { Button } from "@/components/ui/button"
import { File, ArrowLeft } from "lucide-react"
import Upload from "@/components/upload"

interface SidebarItem {
  id: string
  title: string
  content: React.ReactNode
}

const sidebarItems: SidebarItem[] = [
  { id: "1", title: "Item 1", content: <div>Preview content for Item 1</div> },
  { id: "2", title: "Item 2", content: <div>Preview content for Item 2</div> },
  { id: "3", title: "Item 3", content: <div>Preview content for Item 3</div> },
]

export default function CustomSidebar() {
  const [isWide, setIsWide] = useState(false)
  const [selectedItem, setSelectedItem] = useState<SidebarItem | null>(null)

  const toggleWidth = () => {
    setIsWide(!isWide)
  }

  const handleItemClick = (item: SidebarItem) => {
    setSelectedItem(item)
    setIsWide(true)
  }

  return (
    <div
      className={`h-screen border bg-neutral-900 transition-all duration-500 ease-in-out ${
        isWide ? "w-1/4" : "w-1/12"
      }`}
    >
      <div className="p-2">
        {!isWide ? (
          <>
            {" "}
            <span className="text-neutral-400 p-3 text-sm font-semibold block">
              Features
            </span>
            <Button
              onClick={toggleWidth}
              className="p-2 bg-transparent text-white hover:bg-neutral-700 transition-all duration-300 ease-in-out"
            >
              <File width={24} height={24} />
              Upload Files
            </Button>
          </>
        ) : (
          <>
            {" "}
            <Button
              onClick={toggleWidth}
              className="p-2 bg-transparent text-white hover:bg-neutral-700 transition-all duration-300 ease-in-out"
            >
              <ArrowLeft width={24} height={24} />
            </Button>
            <Upload />
          </>
        )}
      </div>
    </div>
  )
}
