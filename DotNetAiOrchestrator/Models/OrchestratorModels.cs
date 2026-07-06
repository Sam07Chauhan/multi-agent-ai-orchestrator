namespace DotNetAiOrchestrator.Models;

public enum ActionType 
{ 
    IMAGE_EDIT, 
    IMAGE_CREATE, 
    DATABASE_QUERY, 
    WEB_BROWSE, 
    UNKNOWN 
}

public class OrchestratorRequest
{
    public IFormFile? File { get; set; }
    public string UserQuery { get; set; } = string.Empty;
    public string? Schema { get; set; }
}

public class OrchestratorResponse
{
    public string ActionPerformed { get; set; } = string.Empty;
    public string DataType { get; set; } = "TEXT"; // TEXT, IMAGE_BASE64, JSON_TABLE
    public object? Content { get; set; }
}