// Ensure aapka sahi namespace yahan ho

var builder = WebApplication.CreateBuilder(args);

// --- SERVICES REGISTRATION ---
builder.Services.AddControllers(); // API Controllers run karne ke liye zaroori hai

// ⚡ FIX: Named HttpClient configure kiya jo Python FastAPI Orchestrator se communicate karega
builder.Services.AddHttpClient("PythonAiClient", client =>
{
    client.BaseAddress = new Uri("http://localhost:8000/"); // Python server port framework address
    client.Timeout = TimeSpan.FromMinutes(15); // ⚡ Heavy Image Inpainting generation ke liye timeout 5 minutes kiya
});

builder.Services.AddScoped<AiOrchestratorService>();

// React UI dev environment communication allowance
builder.Services.AddCors(options =>
{
    options.AddPolicy("AllowReact", policy =>
        policy.WithOrigins("http://localhost:5173")
              .AllowAnyMethod()
              .AllowAnyHeader());
});

// Learn more about configuring OpenAPI at https://aka.ms/aspnet/openapi
builder.Services.AddOpenApi();

var app = builder.Build();

// --- HTTP REQUEST PIPELINE ---

// CORS Middleware ko pipeline mein sabse upar lagayein takki React block na ho
app.UseCors("AllowReact");

if (app.Environment.IsDevelopment())
{
    app.MapOpenApi();
}

// Local testing ke liye aap ise comment bhi kar sakte hain agar http vs https ka issue aaye
app.UseHttpsRedirection();

app.UseAuthorization();

// ⚡ CRITICAL: Yeh line aapke Controllers (OrchestratorController) ko active karegi
app.MapControllers(); 

// --- TEMPLATE WEATHER BACKUP (Aap chahein toh ise hata bhi sakte hain) ---
var summaries = new[]
{
    "Freezing", "Bracing", "Chilly", "Cool", "Mild", "Warm", "Balmy", "Hot", "Sweltering", "Scorching"
};

app.MapGet("/weatherforecast", () =>
{
    var forecast =  Enumerable.Range(1, 5).Select(index =>
        new WeatherForecast
        (
            DateOnly.FromDateTime(DateTime.Now.AddDays(index)),
            Random.Shared.Next(-20, 55),
            summaries[Random.Shared.Next(summaries.Length)]
        ))
        .ToArray();
    return forecast;
})
.WithName("GetWeatherForecast");

app.Run();

record WeatherForecast(DateOnly Date, int TemperatureC, string? Summary)
{
    public int TemperatureF => 32 + (int)(TemperatureC / 0.5556);
}