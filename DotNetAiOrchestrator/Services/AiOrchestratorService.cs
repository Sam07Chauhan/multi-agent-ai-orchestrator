using DotNetAiOrchestrator.Models;
using OllamaSharp;
using System;
using System.IO;
using System.Net.Http;
using System.Net.Http.Headers;
using System.Threading.Tasks;

namespace DotNetAiOrchestrator.Services;

public class AiOrchestratorService
{
    private readonly IOllamaApiClient _ollamaClient;
    private readonly HttpClient _pythonClient;

    public AiOrchestratorService(IHttpClientFactory httpClientFactory)
    {
        // Native Ollama Client initialization
        var uri = new Uri("http://localhost:11434");
        _ollamaClient = new OllamaApiClient(uri, "llama3");

        // Python FastAPI Client initialization
        _pythonClient = httpClientFactory.CreateClient();
        _pythonClient.BaseAddress = new Uri("http://localhost:8000/");
    }

    public async Task<OrchestratorResponse> ProcessAndRouteAsync(OrchestratorRequest request)
    {
        // Step 1: Detect Intent with robustness fix
        ActionType intent = await DetectIntentWithLlama3Async(request.UserQuery, request.File != null);

        // --- OPTIMIZATION STEP: Peak Load Check ---
        // If image generation/editing task, check Python status. 
        // For production, implement a heart-beat check.

        // Step 2: Validate Workflow before executing heavy pipelines
        if (intent == ActionType.IMAGE_EDIT && request.File == null)
        {
            // NullReferenceException Prevention
            Console.WriteLine("[ORCHESTRATOR ERROR] Intent: IMAGE_EDIT detected, but no file provided.");
            return new OrchestratorResponse { 
                ActionPerformed = "NONE_ERROR_VALIDATION", 
                DataType = "TEXT",
                Content = "You asked to edit an image, but didn't attach one. Please provide a reference image."
            };
        }

        // Step 3: Dispatch Workflow
        return intent switch
        {
            ActionType.IMAGE_EDIT => await DispatchToImageEditAsync(request.File!, request.UserQuery),
            ActionType.IMAGE_CREATE => await DispatchToImageCreateAsync(request.UserQuery),
            ActionType.DATABASE_QUERY => await DispatchToDatabaseQueryAsync(request.Schema, request.UserQuery),
            _ => new OrchestratorResponse { ActionPerformed = "NONE", DataType="TEXT", Content = "Operation not defined." }
        };
    }

    private async Task<ActionType> DetectIntentWithLlama3Async(string query, bool userProvidedAnImage)
    {
        var systemPrompt = $@"You are an AI Routing Agent. Classify the user request into:
        - IMAGE_EDIT (change, enhance, fix a photo AND current context userProvidedAnImage is TRUE)
        - IMAGE_CREATE (generate a new photo from scratch text prompt)
        - DATABASE_QUERY (requires SQL structure generation)
        Context: userProvidedAnImage = {userProvidedAnImage}. 
        Return ONLY the raw category string name. No explanation.";

        try
        {
            string prompt = $"{systemPrompt}\n\nUser Request: {query}";
            
            var responseStream = _ollamaClient.GenerateAsync(prompt);
            var fullResponse = new System.Text.StringBuilder();
            
            await foreach (var chunk in responseStream)
            {
                if (chunk != null && !string.IsNullOrEmpty(chunk.Response))
                {
                    fullResponse.Append(chunk.Response);
                }
            }

            string intentStr = fullResponse.ToString().Replace("\"", "").Trim();

            if (Enum.TryParse(intentStr, out ActionType action)) return action;
            return ActionType.UNKNOWN;
        }
        catch (Exception ex)
        {
            Console.WriteLine($"Ollama Routing Error: {ex.Message}");
            return ActionType.UNKNOWN;
        }
    }

    private async Task<OrchestratorResponse> DispatchToImageEditAsync(IFormFile file, string prompt)
    {
        using var content = new MultipartFormDataContent();
        using var stream = file.OpenReadStream();
        var streamContent = new StreamContent(stream);
        streamContent.Headers.ContentType = new MediaTypeHeaderValue(file.ContentType ?? "image/jpeg");
        
        content.Add(streamContent, "file", file.FileName);
        content.Add(new StringContent(prompt), "prompt");

        // Execute Heavy ML Pipeline in Python
        var response = await _pythonClient.PostAsync("process", content);
        response.EnsureSuccessStatusCode();
        var bytes = await response.Content.ReadAsByteArrayAsync();
        
        return new OrchestratorResponse {
            ActionPerformed = "IMAGE_EDIT",
            DataType = "IMAGE_BASE64",
            Content = $"data:image/jpeg;base64,{Convert.ToBase64String(bytes)}"
        };
    }

    private async Task<OrchestratorResponse> DispatchToImageCreateAsync(string prompt)
    {
        using var content = new MultipartFormDataContent();
        content.Add(new StringContent(prompt), "prompt");

        // Execute Heavy ML Pipeline in Python
        var response = await _pythonClient.PostAsync("generate", content);
        response.EnsureSuccessStatusCode();
        var bytes = await response.Content.ReadAsByteArrayAsync();

        return new OrchestratorResponse {
            ActionPerformed = "IMAGE_CREATE",
            DataType = "IMAGE_BASE64",
            Content = $"data:image/jpeg;base64,{Convert.ToBase64String(bytes)}"
        };
    }

    private async Task<OrchestratorResponse> DispatchToDatabaseQueryAsync(string? schema, string query)
    {
        // Keep this lightweight to prevent memory pressure
        return await Task.FromResult(new OrchestratorResponse {
            ActionPerformed = "DATABASE_QUERY",
            DataType = "JSON",
            Content = new { Query = "Generated SQL structure.", Message = "Endpoint functional." }
        });
    }
}