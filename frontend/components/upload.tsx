"use client"

import { useState, useRef, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Trash, Terminal, X, Check } from "lucide-react"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import apiClient from "@/lib/api-client"

export default function UploadPage() {
  const [file, setFile] = useState<File | null>(null)
  const [preview, setPreview] = useState<string | null>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<string | null>(null)

  useEffect(() => {
    if (error || success) {
      const timer = setTimeout(() => {
        setError(null)
        setSuccess(null)
      }, 5000)
      return () => clearTimeout(timer)
    }
  }, [error, success])

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = event.target.files?.[0]
    if (selectedFile) {
      setFile(selectedFile)
      generatePreview(selectedFile)
    }
    // Reset the file input value
    if (event.target) {
      event.target.value = ""
    }
  }

  const handleFileSubmit = async () => {
    if (!file) {
      setError("No file selected.")
      return
    }

    try {
      const formData = new FormData()
      formData.append("file", file)
      const response = await fetch("http://localhost:3000/upload", {
        method: "POST",
        body: formData,
      })
      if (!response.ok) {
        throw new Error("Failed to upload file")
      }

      if (response.error) {
        throw new Error(response.error)
      } else if (response.success) {
        setSuccess(response.success)
      }
    } catch (error) {
      setError({ error })
    }
    // Handle file upload logic here
    setSuccess("File uploaded successfully.")
    setError(null)
  }

  const generatePreview = (file: File) => {
    const reader = new FileReader()
    reader.onload = (e) => {
      const content = e.target?.result as string
      setPreview(content)
    }

    if (file.type === "application/pdf") {
      setPreview(URL.createObjectURL(file))
    } else {
      reader.readAsText(file)
    }
  }

  const handleDragOver = (event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault()
  }

  const handleDrop = (event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault()
    const droppedFile = event.dataTransfer.files[0]
    if (droppedFile) {
      setFile(droppedFile)
      generatePreview(droppedFile)
    }
  }

  const deleteFile = () => {
    setFile(null)
    setPreview(null)
    if (fileInputRef.current) {
      fileInputRef.current.value = ""
    }
  }

  return (
    <>
      <div className="container mx-auto px-4 py-8">
        <Card className="max-w-2xl mx-auto">
          <CardHeader>
            <CardTitle className="text-center">File Upload</CardTitle>
          </CardHeader>
          <CardContent>
            {file && (
              <>
                <div className="mt-4 flex items-center justify-between">
                  <div>
                    <h3 className="text-lg font-semibold mb-2">
                      Selected File:
                    </h3>
                    <p>{file.name}</p>
                  </div>
                  <Trash
                    onClick={deleteFile}
                    className="w-6 h-6 text-red-700 cursor-pointer"
                  />
                </div>
                <div className="mt-4 items-center justify-center w-full text-center">
                  <Button onClick={handleFileSubmit}>Upload File</Button>
                </div>
              </>
            )}
            {preview && (
              <div className="mt-4">
                <h3 className="text-lg font-semibold mb-2">Preview:</h3>
                {file?.type === "application/pdf" ? (
                  <iframe
                    src={preview}
                    className="w-full h-96 border rounded"
                  />
                ) : (
                  <pre className="bg-muted p-4 rounded-lg overflow-auto max-h-96">
                    {preview}
                  </pre>
                )}
              </div>
            )}
            {!file & !preview && (
              <div
                className="flex flex-col border-2 border-dashed border-primary rounded-lg p-8 items-center justify-center text-center mt-4 mb-4"
                onDragOver={handleDragOver}
                onDrop={handleDrop}
              >
                <Input
                  type="file"
                  accept=".txt,.js,.py,.csv,.pdf"
                  onChange={handleFileChange}
                  className="hidden"
                  ref={fileInputRef}
                />
                <Label htmlFor="file-upload" className="cursor-pointer">
                  Drag and drop a file here, or click to select a file
                </Label>
                <Button
                  onClick={() => fileInputRef.current?.click()}
                  variant="outline"
                  className="mt-4"
                >
                  Select File
                </Button>
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Card for error */}
      {error && (
        <div className="fixed top-4 right-4 z-50">
          <Alert className="relative w-[300px] items-center justify-center border-red-500">
            <Terminal className="h-4 w-4" />
            <AlertTitle>Error occured while uploading File!</AlertTitle>
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        </div>
      )}

      {/* Card for success */}
      {success && (
        <div className="fixed top-4 right-4 z-50">
          <Alert className="relative w-[300px] items-center justify-center border-green-500">
            <Check className="h-4 w-4" />
            <AlertTitle>Heads up!</AlertTitle>
            <AlertDescription>{success}</AlertDescription>
          </Alert>
        </div>
      )}
    </>
  )
}
