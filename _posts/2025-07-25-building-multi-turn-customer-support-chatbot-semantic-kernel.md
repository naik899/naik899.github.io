---
layout: post
title: "Building a Multi-Turn Customer Support Chatbot with Semantic Kernel (C#)"
date: 2025-08-03
categories: [AI, Microsoft, .NET, Chatbot]
tags: [semantic-kernel, chatbot, customer-support, ai-development, csharp]
author: Ravindra Naik
---

# Building a Multi-Turn Customer Support Chatbot with Semantic Kernel (C#)

Customer support chatbots have evolved significantly with the advent of AI technologies. Modern chatbots need to handle complex, multi-turn conversations while maintaining context and providing accurate, helpful responses. In this article, we'll explore how to build a sophisticated customer support chatbot using Microsoft's Semantic Kernel framework in C#.

## TL;DR

This article demonstrates how to build a multi-turn customer support chatbot using Semantic Kernel (C#) that can handle complex conversations, maintain context across multiple interactions, and provide intelligent responses based on customer queries. We'll cover conversation management, context preservation, and integration with external knowledge bases.

## Understanding Multi-Turn Conversations

Multi-turn conversations are essential for effective customer support. Unlike simple Q&A systems, multi-turn chatbots can:

- **Maintain Context**: Remember previous interactions within a conversation
- **Handle Complex Queries**: Break down complex requests into multiple steps
- **Provide Personalized Responses**: Adapt responses based on conversation history
- **Escalate Appropriately**: Identify when human intervention is needed

## Setting Up the Project

First, let's set up a new .NET project with the necessary dependencies:

```bash
dotnet new console -n CustomerSupportChatbot
cd CustomerSupportChatbot
dotnet add package Microsoft.SemanticKernel
dotnet add package Microsoft.SemanticKernel.Connectors.OpenAI
dotnet add package Microsoft.Extensions.DependencyInjection
dotnet add package Microsoft.Extensions.Logging
```

## Core Architecture

Our chatbot will consist of several key components:

1. **Conversation Manager**: Handles conversation state and context
2. **Intent Recognition**: Identifies customer intent and required actions
3. **Response Generator**: Creates appropriate responses using AI
4. **Knowledge Base Integration**: Connects to product/service information
5. **Escalation Handler**: Manages handoffs to human agents

## Implementing the Conversation Manager

The conversation manager is the heart of our multi-turn chatbot:

```csharp
public class ConversationManager
{
    private readonly Dictionary<string, ConversationContext> _conversations;
    private readonly Kernel _kernel;
    private readonly ILogger<ConversationManager> _logger;

    public ConversationManager(Kernel kernel, ILogger<ConversationManager> logger)
    {
        _conversations = new Dictionary<string, ConversationContext>();
        _kernel = kernel;
        _logger = logger;
    }

    public async Task<ChatResponse> ProcessMessageAsync(string conversationId, string userMessage)
    {
        // Get or create conversation context
        var context = GetOrCreateConversation(conversationId);
        
        // Add user message to history
        context.AddUserMessage(userMessage);
        
        // Analyze intent and generate response
        var response = await GenerateResponseAsync(context, userMessage);
        
        // Add bot response to history
        context.AddBotMessage(response.Message);
        
        return response;
    }

    private ConversationContext GetOrCreateConversation(string conversationId)
    {
        if (!_conversations.ContainsKey(conversationId))
        {
            _conversations[conversationId] = new ConversationContext(conversationId);
        }
        return _conversations[conversationId];
    }
}
```

## Conversation Context Management

The conversation context maintains the state and history of each conversation:

```csharp
public class ConversationContext
{
    public string ConversationId { get; }
    public List<ChatMessage> MessageHistory { get; }
    public Dictionary<string, object> Variables { get; }
    public DateTime LastActivity { get; private set; }

    public ConversationContext(string conversationId)
    {
        ConversationId = conversationId;
        MessageHistory = new List<ChatMessage>();
        Variables = new Dictionary<string, object>();
        LastActivity = DateTime.UtcNow;
    }

    public void AddUserMessage(string message)
    {
        MessageHistory.Add(new ChatMessage("user", message));
        LastActivity = DateTime.UtcNow;
    }

    public void AddBotMessage(string message)
    {
        MessageHistory.Add(new ChatMessage("assistant", message));
        LastActivity = DateTime.UtcNow;
    }

    public string GetConversationSummary()
    {
        // Create a summary of the conversation for context
        var recentMessages = MessageHistory.TakeLast(10);
        return string.Join("\n", recentMessages.Select(m => $"{m.Role}: {m.Content}"));
    }
}
```

## Intent Recognition and Response Generation

The core of our chatbot's intelligence lies in understanding user intent and generating appropriate responses:

```csharp
public class ChatbotService
{
    private readonly Kernel _kernel;
    private readonly IKnowledgeBaseService _knowledgeBase;
    private readonly ILogger<ChatbotService> _logger;

    public ChatbotService(Kernel kernel, IKnowledgeBaseService knowledgeBase, ILogger<ChatbotService> logger)
    {
        _kernel = kernel;
        _knowledgeBase = knowledgeBase;
        _logger = logger;
    }

    public async Task<ChatResponse> GenerateResponseAsync(ConversationContext context, string userMessage)
    {
        try
        {
            // Analyze user intent
            var intent = await AnalyzeIntentAsync(userMessage, context);
            
            // Generate response based on intent
            var response = await GenerateIntentBasedResponseAsync(intent, context);
            
            // Check if escalation is needed
            if (ShouldEscalate(intent, context))
            {
                response.EscalationRequired = true;
                response.EscalationReason = "Complex query requiring human assistance";
            }
            
            return response;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error generating response for conversation {ConversationId}", context.ConversationId);
            return new ChatResponse
            {
                Message = "I apologize, but I'm experiencing technical difficulties. Please try again or contact our support team.",
                EscalationRequired = true,
                EscalationReason = "Technical error in response generation"
            };
        }
    }

    private async Task<IntentAnalysis> AnalyzeIntentAsync(string message, ConversationContext context)
    {
        var prompt = $@"
        Analyze the following customer message and determine the intent:
        
        Customer Message: {message}
        Conversation Context: {context.GetConversationSummary()}
        
        Possible intents:
        - Product Information
        - Technical Support
        - Billing Inquiry
        - Account Management
        - Complaint
        - General Inquiry
        
        Return the intent and confidence level (0-1).
        ";

        var result = await _kernel.InvokePromptAsync(prompt);
        return ParseIntentResult(result.ToString());
    }
}
```

## Knowledge Base Integration

Integrating with a knowledge base allows the chatbot to provide accurate, up-to-date information:

```csharp
public interface IKnowledgeBaseService
{
    Task<string> SearchAsync(string query);
    Task<List<string>> GetRelatedArticlesAsync(string topic);
    Task<bool> UpdateArticleAsync(string articleId, string content);
}

public class KnowledgeBaseService : IKnowledgeBaseService
{
    private readonly HttpClient _httpClient;
    private readonly string _apiEndpoint;

    public KnowledgeBaseService(HttpClient httpClient, IConfiguration configuration)
    {
        _httpClient = httpClient;
        _apiEndpoint = configuration["KnowledgeBase:ApiEndpoint"];
    }

    public async Task<string> SearchAsync(string query)
    {
        var response = await _httpClient.PostAsJsonAsync($"{_apiEndpoint}/search", new { query });
        response.EnsureSuccessStatusCode();
        
        var result = await response.Content.ReadFromJsonAsync<SearchResult>();
        return result?.Content ?? "No relevant information found.";
    }

    public async Task<List<string>> GetRelatedArticlesAsync(string topic)
    {
        var response = await _httpClient.GetAsync($"{_apiEndpoint}/related/{Uri.EscapeDataString(topic)}");
        response.EnsureSuccessStatusCode();
        
        var articles = await response.Content.ReadFromJsonAsync<List<Article>>();
        return articles?.Select(a => a.Title).ToList() ?? new List<string>();
    }
}
```

## Escalation and Human Handoff

An important aspect of customer support chatbots is knowing when to escalate to human agents:

```csharp
public class EscalationService
{
    private readonly ILogger<EscalationService> _logger;
    private readonly IAgentAssignmentService _agentAssignment;

    public EscalationService(ILogger<EscalationService> logger, IAgentAssignmentService agentAssignment)
    {
        _logger = logger;
        _agentAssignment = agentAssignment;
    }

    public async Task<EscalationResult> HandleEscalationAsync(ConversationContext context, string reason)
    {
        _logger.LogInformation("Escalating conversation {ConversationId} for reason: {Reason}", 
            context.ConversationId, reason);

        // Assign to available agent
        var agent = await _agentAssignment.AssignAgentAsync(context.ConversationId);
        
        // Create escalation record
        var escalation = new EscalationRecord
        {
            ConversationId = context.ConversationId,
            Reason = reason,
            AssignedAgent = agent,
            EscalationTime = DateTime.UtcNow,
            ConversationSummary = context.GetConversationSummary()
        };

        // Notify agent
        await NotifyAgentAsync(agent, escalation);

        return new EscalationResult
        {
            Success = true,
            AssignedAgent = agent,
            EstimatedWaitTime = await GetEstimatedWaitTimeAsync()
        };
    }
}
```

## Main Application Setup

Here's how to wire everything together in the main application:

```csharp
class Program
{
    static async Task Main(string[] args)
    {
        // Setup dependency injection
        var services = new ServiceCollection();
        ConfigureServices(services);
        
        var serviceProvider = services.BuildServiceProvider();
        
        // Get chatbot service
        var chatbot = serviceProvider.GetRequiredService<ConversationManager>();
        
        // Start conversation loop
        await RunChatbotAsync(chatbot);
    }

    static void ConfigureServices(IServiceCollection services)
    {
        // Configure Semantic Kernel
        var kernel = Kernel.CreateBuilder()
            .AddOpenAIChatCompletion("gpt-4", Environment.GetEnvironmentVariable("OPENAI_API_KEY"))
            .Build();
        
        services.AddSingleton(kernel);
        
        // Register services
        services.AddHttpClient<IKnowledgeBaseService, KnowledgeBaseService>();
        services.AddScoped<ConversationManager>();
        services.AddScoped<ChatbotService>();
        services.AddScoped<EscalationService>();
        services.AddScoped<IAgentAssignmentService, AgentAssignmentService>();
        
        // Configure logging
        services.AddLogging(builder =>
        {
            builder.AddConsole();
            builder.AddDebug();
        });
    }

    static async Task RunChatbotAsync(ConversationManager chatbot)
    {
        Console.WriteLine("Customer Support Chatbot Started");
        Console.WriteLine("Type 'exit' to quit");
        
        var conversationId = Guid.NewGuid().ToString();
        
        while (true)
        {
            Console.Write("\nCustomer: ");
            var input = Console.ReadLine();
            
            if (string.IsNullOrEmpty(input) || input.ToLower() == "exit")
                break;
            
            try
            {
                var response = await chatbot.ProcessMessageAsync(conversationId, input);
                Console.WriteLine($"\nBot: {response.Message}");
                
                if (response.EscalationRequired)
                {
                    Console.WriteLine($"\n[Escalating to human agent: {response.EscalationReason}]");
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"\nError: {ex.Message}");
            }
        }
    }
}
```

## Advanced Features

### Conversation Analytics

Track conversation metrics to improve the chatbot's performance:

```csharp
public class ConversationAnalytics
{
    public async Task TrackConversationAsync(ConversationContext context, ChatResponse response)
    {
        var metrics = new ConversationMetrics
        {
            ConversationId = context.ConversationId,
            Duration = DateTime.UtcNow - context.CreatedAt,
            MessageCount = context.MessageHistory.Count,
            EscalationRequired = response.EscalationRequired,
            UserSatisfaction = await CalculateSatisfactionAsync(context)
        };
        
        await SaveMetricsAsync(metrics);
    }
}
```

### Multi-Language Support

Extend the chatbot to support multiple languages:

```csharp
public class MultiLanguageService
{
    private readonly Kernel _kernel;
    private readonly Dictionary<string, string> _languagePrompts;

    public async Task<string> TranslateAsync(string text, string targetLanguage)
    {
        var prompt = $"Translate the following text to {targetLanguage}:\n{text}";
        var result = await _kernel.InvokePromptAsync(prompt);
        return result.ToString();
    }

    public async Task<string> DetectLanguageAsync(string text)
    {
        var prompt = $"Detect the language of the following text:\n{text}";
        var result = await _kernel.InvokePromptAsync(prompt);
        return result.ToString();
    }
}
```

## Best Practices

When building multi-turn customer support chatbots, consider these best practices:

1. **Context Management**: Always maintain conversation context and history
2. **Intent Recognition**: Use sophisticated intent analysis for better understanding
3. **Graceful Degradation**: Handle errors gracefully and provide fallback options
4. **Escalation Strategy**: Implement clear escalation criteria and processes
5. **Performance Monitoring**: Track key metrics to continuously improve
6. **Security**: Implement proper authentication and data protection
7. **Testing**: Thoroughly test with various conversation scenarios

## Conclusion

Building a multi-turn customer support chatbot with Semantic Kernel (C#) provides a powerful foundation for intelligent customer interactions. By implementing proper conversation management, intent recognition, and escalation handling, you can create a chatbot that significantly improves customer support efficiency while maintaining high satisfaction levels.

The key to success lies in understanding that customer support conversations are complex and require sophisticated handling of context, intent, and escalation. With the right architecture and implementation, your chatbot can handle most customer inquiries while seamlessly escalating complex cases to human agents.

Remember to continuously monitor and improve your chatbot based on real-world usage data and customer feedback. The combination of Semantic Kernel's AI capabilities with robust conversation management creates a powerful tool for modern customer support operations. 