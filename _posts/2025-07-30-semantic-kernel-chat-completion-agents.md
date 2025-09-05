---
layout: post
title: "Using Semantic Kernel Chat Completion Agents for Multi-Turn Conversational Bots"
date: 2025-07-30
categories: [AI, Microsoft, .NET, Chatbot]
tags: [semantic-kernel, chat-completion, multi-turn, agents, csharp]
author: Ravindra Naik
---

# Using Semantic Kernel Chat Completion Agents for Multi-Turn Conversational Bots

Building engaging conversational experiences requires more than single question and answer prompts. Semantic Kernel's **chat completion agents** provide stateful interactions that make it possible to create multi-turn bots capable of juggling several conversations.

## TL;DR

1. Install Semantic Kernel and the OpenAI connectors.
2. Create a `ChatCompletionAgent` and wire it to the OpenAI chat completion service.
3. Maintain a conversation context so the bot remembers previous turns.
4. Reuse the agent across multiple conversations by tracking a history per user.

## Project Setup

Create a new console project and add the required NuGet packages:

```bash
dotnet new console -n MultiTurnBot
cd MultiTurnBot
dotnet add package Microsoft.SemanticKernel
dotnet add package Microsoft.SemanticKernel.Agents
```

## Creating the Agent

```csharp
var builder = Kernel.CreateBuilder();
builder.AddOpenAIChatCompletion("gpt-4o", Environment.GetEnvironmentVariable("OPENAI_API_KEY"));
var kernel = builder.Build();

var agent = new ChatCompletionAgent(kernel)
{
    Instructions = "You are a friendly assistant that answers questions about our products."
};
```

The agent wraps the chat completion service and keeps a message history internally.

## Running a Multi-Turn Conversation

```csharp
var conversation = agent.CreateConversation();

while (true)
{
    Console.Write("User: ");
    var input = Console.ReadLine();
    if (string.IsNullOrEmpty(input)) break;

    conversation.AddUserMessage(input);
    var reply = await agent.GetResponseAsync(conversation);
    Console.WriteLine($"Bot: {reply.Message}");
}
```

`CreateConversation` returns a context object. The same agent can spawn many of these allowing multiple people to chat with the bot concurrently.

## Managing Multiple Conversations

To handle several chats at once, store conversations in a dictionary keyed by a user or session id:

```csharp
var conversations = new Dictionary<string, ChatHistory>();

ChatHistory GetOrCreate(string id)
{
    if (!conversations.TryGetValue(id, out var history))
    {
        history = agent.CreateConversation();
        conversations[id] = history;
    }
    return history;
}
```

Each history instance tracks its own messages so context is preserved for every user.

## Best Practices

- **Persist History**: Save the message history if conversations need to survive restarts.
- **Use System Prompts**: Seed conversations with instructions that define the bot's personality and scope.
- **Limit Tokens**: Trim older messages to avoid hitting model token limits.
- **Monitor Usage**: Track latency and cost when running large numbers of concurrent chats.

## Conclusion

Semantic Kernel's chat completion agents provide a straightforward way to build multi-turn, multi-user conversational bots. By encapsulating message history and simplifying model calls, they let you focus on the unique logic of your application rather than plumbing. Combine agents with memory, planning, and external APIs to create rich conversational experiences.
