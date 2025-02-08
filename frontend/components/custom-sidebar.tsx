"use client"

import type React from "react"
import { useState } from "react"
import { Button } from "@/components/ui/button"

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
    <div className={`h-screen border border-gray-700 transition-all duration-300 ease-in-out ${isWide ? "w-1/3" : "w-1/6"}`}>
      <div className="p-4">
        <Button onClick={toggleWidth} className="mb-4">
          {isWide ? "Narrow Sidebar" : "Widen Sidebar"}
        </Button>
        <div className="space-y-2">
          {sidebarItems.map((item) => (
            <Button
              key={item.id}
              onClick={() => handleItemClick(item)}
              variant="ghost"
              className="w-full justify-start"
            >
              {item.title}
            </Button>
          ))}
        </div>
      </div>
      {selectedItem && isWide && (
        <div className="p-4 bg-white rounded-lg shadow mt-4 mx-2">
          <h3 className="text-lg font-semibold mb-2">{selectedItem.title}</h3>
          {selectedItem.content}
        </div>
      )}
    </div>
  )
}

