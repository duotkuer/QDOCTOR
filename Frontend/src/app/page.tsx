'use client'
import ChatCard from "@/components/chat-input";
import { IconInnerShadowTop } from "@tabler/icons-react";
import { useState } from "react";

interface Message {
  id: number;
  type: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  sources?: string[];
}

export default function Page({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
    const [messages, setMessages] = useState<Message[]>([]);
    const [isTyping, setIsTyping] = useState(false);

  const handleSubmit = async (message: string) => {
    if (!message.trim()) return;

    const userMessage: Message = {
      id: Date.now(),
      type: 'user',
      content: message,
      timestamp: new Date()
    };
    setMessages(prev => [...prev, userMessage]);
    setIsTyping(true);

    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'An error occurred');
      }

      const data = await response.json();

      let responseContent = "Sorry, I couldn't process the response.";
      let sources: string[] = [];

      if (data.answer) {
        responseContent = data.answer;
        sources = data.context?.map((c: any) => c.file_name).filter(Boolean) || [];
      }

      const assistantMessage: Message = {
        id: Date.now() + 1,
        type: 'assistant',
        content: responseContent,
        sources: sources,
        timestamp: new Date()
      };
      setMessages(prev => [...prev, assistantMessage]);
      console.log(assistantMessage);
      

    } catch (error) {
      const errorMessage: Message = {
        id: Date.now() + 1,
        type: 'assistant',
        content: `Sorry, I encountered an error: ${error instanceof Error ? error.message : String(error)}`,
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsTyping(false);
    }
  };
  return (
    <>
      <div className="w-full flex flex-col text-center gap-5">
        <div className="flex flex-col justify-center items-center">
          <IconInnerShadowTop className="!size-20" />
          <h1 className="font-bold text-6xl text-sidebar-accent-foreground">QDoctor AI</h1>
        </div>
        <ChatCard onMessageSent={handleSubmit} />
      </div>
    </>
  )
}
