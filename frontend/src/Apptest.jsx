import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Button } from '@/components/ui/button';
import { Loader2 } from 'lucide-react';

const App = () => {
  const [userInput, setUserInput] = useState('');
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!userInput.trim()) return;

    // Add user message to chat
    const newUserMessage = {
      type: 'user',
      content: userInput,
      timestamp: new Date().toLocaleTimeString()
    };
    
    setMessages(prev => [...prev, newUserMessage]);
    setIsLoading(true);

    // Simulate API call with timeout
    setTimeout(() => {
      // Add mock response
      const mockResponse = {
        type: 'assistant',
        content: `Mock response for: ${userInput}`,
        timestamp: new Date().toLocaleTimeString()
      };
      setMessages(prev => [...prev, mockResponse]);
      setIsLoading(false);
      setUserInput('');
    }, 1000);
  };

  return (
    <div className="max-w-4xl mx-auto p-4">
      <Card className="w-full">
        <CardHeader>
          <CardTitle>PLC Code Generator</CardTitle>
        </CardHeader>
        <CardContent>
          {/* Chat messages area */}
          <ScrollArea className="h-[400px] mb-4 p-4 border rounded-lg">
            {messages.map((message, index) => (
              <div
                key={index}
                className={`mb-4 ${
                  message.type === 'user' 
                    ? 'ml-auto text-right' 
                    : 'mr-auto'
                }`}
              >
                <div
                  className={`inline-block max-w-[80%] p-3 rounded-lg ${
                    message.type === 'user'
                      ? 'bg-blue-500 text-white'
                      : message.type === 'system'
                      ? 'bg-red-100 text-red-800'
                      : 'bg-gray-100'
                  }`}
                >
                  <p className="text-sm">{message.content}</p>
                  <span className="text-xs opacity-75">{message.timestamp}</span>
                </div>
              </div>
            ))}
          </ScrollArea>

          {/* Input area */}
          <form onSubmit={handleSubmit} className="flex gap-2">
            <textarea
              value={userInput}
              onChange={(e) => setUserInput(e.target.value)}
              placeholder="Type your requirements here..."
              className="flex-1 p-2 border rounded-lg resize-none h-24"
              disabled={isLoading}
            />
            <Button 
              type="submit" 
              disabled={isLoading || !userInput.trim()}
              className="h-24 w-24"
            >
              {isLoading ? (
                <Loader2 className="h-6 w-6 animate-spin" />
              ) : (
                'Generate'
              )}
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  );
};

export default App;