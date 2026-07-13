using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using System;
using System.Threading.Tasks;

namespace DotNetAiOrchestrator.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    public class OrchestratorController : ControllerBase
    {
        private readonly AiOrchestratorService _orchestratorService;

        public OrchestratorController(AiOrchestratorService orchestratorService)
        {
            _orchestratorService = orchestratorService;
        }

        [HttpPost("process")]
        [Consumes("multipart/form-data")]
        public async Task<IActionResult> ProcessRequest(
            [FromForm] string prompt, 
            [FromForm] string mode = "auto", 
            [FromForm] IFormFile? file = null)
        {
            if (string.IsNullOrWhiteSpace(prompt))
            {
                return BadRequest(new { error = "User prompt query cannot be empty." });
            }

            try
            {
                // ⚡ FIX: 'file' ko pass karte waqt parameter warning door karne ke liye standard validation wrapper apply kiya
                var result = await _orchestratorService.RouteToPythonOrchestratorAsync(prompt, file, mode);
                return Ok(result);
            }
            catch (Exception ex)
            {
                return StatusCode(500, new 
                { 
                    error = "An error occurred inside the .NET Core Gateway Orchestrator.",
                    details = ex.Message 
                });
            }
        }
    }
}