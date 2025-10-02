'use client'
import React, { useState, useEffect, useRef } from 'react';
import { Search, Copy, RotateCcw, Share2, ThumbsUp, ThumbsDown, Sparkles, Bot, User, Upload, ArrowUp, Menu } from 'lucide-react';
import ChatCard from '@/components/chat-input';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { useSearchParams } from 'next/navigation';

interface Message {
  id: number;
  type: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  sources?: string[];
}

const MarkdownRenderer = ReactMarkdown as React.FC<{
  children: string;
  remarkPlugins?: any[];
  className?: string;
}>;

const ChatScreen = () => {
  const searchParams = useSearchParams();
  const [messages, setMessages] = useState<Message[]>([]);
  const [isTyping, setIsTyping] = useState(false);
  const [sessionId, setSessionId] = useState<string>('');
  const [isScrollHovered, setIsScrollHovered] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new messages are added
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isTyping]);

  // Initialize chat with URL parameters if coming from home page
  useEffect(() => {
    const urlSessionId = searchParams.get('sessionId');
    const initialMessage = searchParams.get('initialMessage');
    const response = searchParams.get('response');

    if (urlSessionId) {
      setSessionId(urlSessionId);
    }

    if (initialMessage && response) {
      try {
        const parsedResponse = JSON.parse(decodeURIComponent(response));

        // Extract the actual response text from your backend
        let responseContent = "I received your message!"; // fallback
        let sources: string[] = [];

        // Handle your specific backend response structure
        if (parsedResponse.response) {
          responseContent = parsedResponse.response;
          sources = parsedResponse.context_sources || [];
        } else if (parsedResponse.message) {
          responseContent = parsedResponse.message;
        } else if (parsedResponse.content) {
          responseContent = parsedResponse.content;
        } else if (parsedResponse.data) {
          responseContent = parsedResponse.data;
        } else if (typeof parsedResponse === 'string') {
          responseContent = parsedResponse;
        }

        const initialMessages: Message[] = [
          {
            id: 1,
            type: 'user',
            content: decodeURIComponent(initialMessage),
            timestamp: new Date()
          },
          {
            id: 2,
            type: 'assistant',
            content: responseContent,
            sources: sources,
            timestamp: new Date()
          }
        ];
        setMessages(initialMessages);
      } catch (error) {
        console.error('Error parsing response:', error);
        // Fallback to just the user message
        setMessages([
          {
            id: 1,
            type: 'user',
            content: decodeURIComponent(initialMessage),
            timestamp: new Date()
          }
        ]);
      }
    } else {
      // Default welcome message if no initial data
      setMessages([
        {
          id: 1,
          type: 'assistant',
          content: "Hey! How can I help you today?",
          timestamp: new Date()
        }
      ]);
    }
  }, [searchParams]);

  const suggestionButtons = [
    "Search then answer",
    "What's your favorite hobby?",
    "Can you recommend a good book?"
  ];

  const handleMessageSent = (message: string, response: any) => {
    // If response is null, this is the first call to add user message immediately
    if (response === null) {
      const userMessage: Message = {
        id: Date.now(),
        type: 'user',
        content: message,
        timestamp: new Date()
      };
      setMessages(prev => [...prev, userMessage]);
      setIsTyping(true);
      return;
    }

    // This is the second call with the actual response
    setIsTyping(false);

    // Extract response content and sources
    let responseContent = "I received your message!"; // fallback
    let sources: string[] = [];

    if (response.error) {
      responseContent = response.response || "Sorry, I encountered an error. Please try again.";
    } else if (response.response) {
      responseContent = response.response;
      sources = response.context_sources || [];
    } else if (response.message) {
      responseContent = response.message;
    } else if (response.content) {
      responseContent = response.content;
    } else if (response.data) {
      responseContent = response.data;
    } else if (typeof response === 'string') {
      responseContent = response;
    }

    // Add assistant response
    const assistantMessage: Message = {
      id: Date.now() + 1,
      type: 'assistant',
      content: responseContent,
      sources: sources,
      timestamp: new Date()
    };
    setMessages(prev => [...prev, assistantMessage]);
  };

  const handleSuggestionClick = (suggestion: string) => {
    // Add user message immediately
    const userMessage: Message = {
      id: Date.now(),
      type: 'user',
      content: suggestion,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setIsTyping(true);

    // Simulate assistant response
    setTimeout(() => {
      const response: Message = {
        id: Date.now() + 1,
        type: 'assistant',
        content: "I'd be happy to help you with that! Let me know if you need any specific information or assistance.",
        timestamp: new Date()
      };
      setMessages(prev => [...prev, response]);
      setIsTyping(false);
    }, 1500);
  };

  return (
    <div className="w-full h-[90dvh] flex flex-col">
      {/* Chat Messages - Scrollable Area with Enhanced Scrollbar */}
      <div
        className="flex-1 overflow-hidden"
        onMouseEnter={() => setIsScrollHovered(true)}
        onMouseLeave={() => setIsScrollHovered(false)}
      >
        <style jsx>{`
          .chat-scrollbar-container {
            overflow-y: auto;
            scrollbar-width: thin;
            scrollbar-color: rgba(156, 163, 175, 0.5) transparent;
          }
          .chat-scrollbar-container::-webkit-scrollbar {
            width: 6px;
            opacity: ${isScrollHovered ? '1' : '0'};
            transition: opacity 0.3s cubic-bezier(0.4, 0, 0.2, 1);
          }
          .chat-scrollbar-container::-webkit-scrollbar-track {
            background: transparent;
          }
          .chat-scrollbar-container::-webkit-scrollbar-thumb {
            background: rgba(156, 163, 175, 0.5);
            border-radius: 3px;
            transition: background 0.2s cubic-bezier(0.4, 0, 0.2, 1);
          }
          .chat-scrollbar-container::-webkit-scrollbar-thumb:hover {
            background: rgba(156, 163, 175, 0.7);
          }
          .chat-scrollbar-container::-webkit-scrollbar-button:vertical:start:decrement {
            display: none !important;
            height: 0 !important;
            width: 0 !important;
          }
          .chat-scrollbar-container::-webkit-scrollbar-button:vertical:end:increment {
            display: none !important;
            height: 0 !important;
            width: 0 !important;
          }
          .chat-scrollbar-container::-webkit-scrollbar-button:horizontal:start:decrement {
            display: none !important;
          }
          .chat-scrollbar-container::-webkit-scrollbar-button:horizontal:end:increment {
            display: none !important;
          }
          .chat-scrollbar-container::-webkit-scrollbar-corner {
            display: none;
          }
        `}</style>
        <div
          className="chat-scrollbar-container h-full"
          tabIndex={0}
          onKeyDown={(e) => {
            if (e.key === 'ArrowUp' || e.key === 'ArrowDown') {
              e.preventDefault()
              const container = e.currentTarget
              const scrollAmount = 40
              if (e.key === 'ArrowUp') {
                container.scrollTop -= scrollAmount
              } else {
                container.scrollTop += scrollAmount
              }
            }
          }}
          onTouchStart={(e) => {
            const touch = e.touches[0]
            const container = e.currentTarget
            container.setAttribute('data-touch-start', touch.clientY.toString())
          }}
          onTouchMove={(e) => {
            e.preventDefault()
            const touch = e.touches[0]
            const container = e.currentTarget
            const startY = parseFloat(container.getAttribute('data-touch-start') || '0')
            const deltaY = startY - touch.clientY
            container.scrollTop += deltaY * 0.5
            container.setAttribute('data-touch-start', touch.clientY.toString())
          }}
        >
          <div className="p-2 py-6 space-y-6 container mx-auto max-w-4xl">
            {messages.map((message) => (
              <div key={message.id} className={`flex items-start space-x-4 ${message.type === 'user' ? 'flex-row-reverse space-x-reverse' : ''}`}>
                <div className="flex-shrink-0 w-8 h-8 rounded-full bg-border flex items-center justify-center">
                  {message.type === 'assistant' ? (
                    <Bot className="w-4 h-4 text-primary" />
                  ) : (
                    <User className="w-4 h-4 text-primary" />
                  )}
                </div>
                <div className={`flex-1 ${message.type === 'user' ? 'text-right' : ''}`}>
                  <div className={`mb-2 max-w-[80%] ${message.type === 'user' ? 'bg-border text-primary px-4 py-2 rounded-lg inline-block ml-auto' : ''}`}>
                    <MarkdownRenderer
                      children={message.content}
                      remarkPlugins={[remarkGfm]}
                      className="prose prose-sm max-w-none"
                    />
                  </div>

                  {/* Show sources if available */}
                  {/* {message.type === 'assistant' && message.sources && message.sources.length > 0 && (
                    <div className="mb-2 text-sm text-gray-500">
                      <div className="font-medium mb-1">Sources:</div>
                      <div className="flex flex-wrap gap-1">
                        {message.sources.map((source, index) => (
                          <span key={index} className="px-2 py-1 bg-gray-100 dark:bg-gray-800 rounded text-xs">
                            {source.replace('.pdf', '')}
                          </span>
                        ))}
                      </div>
                    </div>
                  )} */}

                  {message.type === 'assistant' && (
                    <div className="flex items-center space-x-4 text-gray-500">
                      <button className="cursor-pointer flex items-center space-x-1 hover:text-gray-300 transition-colors">
                        <Copy className="w-4 h-4" />
                        <span className="text-sm">Copy</span>
                      </button>
                      <button className="cursor-pointer flex items-center space-x-1 hover:text-gray-300 transition-colors">
                        <RotateCcw className="w-4 h-4" />
                        <span className="text-sm">Retry</span>
                      </button>
                      <button className="cursor-pointer flex items-center space-x-1 hover:text-gray-300 transition-colors">
                        <Share2 className="w-4 h-4" />
                        <span className="text-sm">Share</span>
                      </button>
                      <div className="cursor-pointer flex items-center space-x-2 ml-4">
                        <button className="hover:text-green-400 transition-colors">
                          <ThumbsUp className="w-4 h-4" />
                        </button>
                        <button className="cursor-pointer hover:text-red-400 transition-colors">
                          <ThumbsDown className="w-4 h-4" />
                        </button>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            ))}

            {isTyping && (
              <div className="flex items-start space-x-4">
                <div className="flex-shrink-0 w-8 h-8 rounded-full bg-border flex items-center justify-center">
                  <Bot className="w-4 h-4 text-primary" />
                </div>
                <div className="flex space-x-1 items-center">
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                </div>
              </div>
            )}

            {/* Suggestion Buttons - Only show if no messages or just welcome message */}
            {messages.length <= 1 && (
              <div className="px-6 py-4">
                <div className="flex flex-wrap flex-col w-fit gap-3">
                  <button
                    onClick={() => handleSuggestionClick("Search then answer")}
                    className="cursor-pointer w-fit flex items-center space-x-2 px-4 py-2 rounded-lg border border-border transition-colors"
                  >
                    <Search className="w-4 h-4" />
                    <span>Search then answer</span>
                  </button>
                  {suggestionButtons.slice(1).map((suggestion, index) => (
                    <button
                      key={index}
                      onClick={() => handleSuggestionClick(suggestion)}
                      className="cursor-pointer w-fit px-4 py-2 rounded-lg border border-border transition-colors"
                    >
                      {suggestion}
                    </button>
                  ))}
                </div>
              </div>
            )}

            {/* Scroll anchor */}
            <div ref={messagesEndRef} />
          </div>
        </div>
      </div>

      {/* Fixed Input Area at Bottom */}
      <div className="flex-shrink-0 border-t border-border">
        <ChatCard onMessageSent={handleMessageSent} />
      </div>
    </div>
  );
};

export default ChatScreen;