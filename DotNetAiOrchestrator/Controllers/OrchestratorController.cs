using DotNetAiOrchestrator.Models;
using DotNetAiOrchestrator.Services;
using Microsoft.AspNetCore.Mvc;

namespace DotNetAiOrchestrator.Controllers;

[ApiController]
[Route("api/[controller]")]
public class OrchestratorController : ControllerBase
{
    private readonly AiOrchestratorService _orchestrator;

    public OrchestratorController(AiOrchestratorService orchestrator)
    {
        _orchestrator = orchestrator;
    }

    [HttpPost("run")]
    public async Task<IActionResult> ExecuteAction([FromForm] OrchestratorRequest request)
    {
        var result = await _orchestrator.ProcessAndRouteAsync(request);
        return Ok(result);
    }
}