using System;
using System.IO;
using System.Net.Http;
using System.Net.Http.Headers;
using System.Text.Json;
using System.Text;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Http;
using Microsoft.Extensions.Configuration;
using MySql.Data.MySqlClient;

public class AiOrchestratorService
{
    private readonly IHttpClientFactory _httpClientFactory;
    private readonly string _connectionString; // Non-nullable variable explicitly initialized

    public AiOrchestratorService(IHttpClientFactory httpClientFactory, IConfiguration configuration)
    {
        _httpClientFactory = httpClientFactory;
        // ⚡ FIX CS8601 & CS8618: Connection string lookup fallback applied safely to prevent null assignment
        _connectionString = configuration.GetConnectionString("DefaultConnection") ?? "";
    }

    public async Task<object> RouteToPythonOrchestratorAsync(string userQuery, IFormFile? imageFile, string requestMode)
    {
        var client = _httpClientFactory.CreateClient("PythonAiClient");
        using var content = new MultipartFormDataContent();

        content.Add(new StringContent(userQuery), "prompt");
        content.Add(new StringContent(requestMode), "mode");

        if (requestMode == "data" || userQuery.ToLower().Contains("database") || userQuery.ToLower().Contains("report"))
        {
            string liveSchema = await FetchLiveSchemaFromMySqlAsync();
            content.Add(new StringContent(liveSchema), "schema");
        }

        if (imageFile != null && imageFile.Length > 0)
        {
            var streamContent = new StreamContent(imageFile.OpenReadStream());
            streamContent.Headers.ContentType = new MediaTypeHeaderValue(imageFile.ContentType);
            content.Add(streamContent, "file", imageFile.FileName);
        }

        var response = await client.PostAsync("orchestrate", content);
        
        if (!response.IsSuccessStatusCode)
        {
            throw new Exception($"Python AI Engine Processing Error: {response.ReasonPhrase}");
        }

        var responseString = await response.Content.ReadAsStringAsync();
        
        // ⚡ FIX CS8603: Deserialized object null fallback protection added
        var result = JsonSerializer.Deserialize<object>(responseString);
        return result ?? new { error = "Empty dynamic object layout signature returned." };
    }

    private async Task<string> FetchLiveSchemaFromMySqlAsync()
    {
        if (string.IsNullOrEmpty(_connectionString))
        {
            return "Fallback Schema: No database connection string detected inside infrastructure layer.";
        }

        var schemaBuilder = new StringBuilder();
        
        try
        {
            using var connection = new MySqlConnection(_connectionString);
            await connection.OpenAsync();

            string query = @"
                SELECT TABLE_NAME, COLUMN_NAME, DATA_TYPE 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_SCHEMA = DATABASE()
                ORDER BY TABLE_NAME, ORDINAL_POSITION;";

            using var command = new MySqlCommand(query, connection);
            using var reader = await command.ExecuteReaderAsync();

            string currentTable = "";
            while (await reader.ReadAsync())
            {
                // ⚡ FIX CS8600: explicit string casts with null verification checks
                string tableName = reader["TABLE_NAME"]?.ToString() ?? "";
                string columnName = reader["COLUMN_NAME"]?.ToString() ?? "";
                string dataType = reader["DATA_TYPE"]?.ToString() ?? "";

                if (currentTable != tableName)
                {
                    if (!string.IsNullOrEmpty(currentTable)) schemaBuilder.Append("); ");
                    currentTable = tableName;
                    schemaBuilder.Append($"Table: {currentTable} (");
                }
                else
                {
                    schemaBuilder.Append(", ");
                }

                schemaBuilder.Append($"{columnName} {dataType}");
            }
            if (!string.IsNullOrEmpty(currentTable)) schemaBuilder.Append(");");

            return schemaBuilder.ToString();
        }
        catch (Exception ex)
        {
            return $"MySQL Schema Extraction Error Fallback: {ex.Message}";
        }
    }
}