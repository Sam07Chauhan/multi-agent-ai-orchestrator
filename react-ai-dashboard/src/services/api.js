/**
 * API Service for communicating with .NET Gateway Orchestrator
 */

const BASE_URL = "http://localhost:5137/api/orchestrator";

export async function processOrchestratorRequest({ prompt, mode, file, signal }) {
  const formData = new FormData();
  formData.append("prompt", prompt);
  formData.append("mode", mode);

  if (file) {
    formData.append("file", file);
  }

  const response = await fetch(`${BASE_URL}/process`, {
    method: "POST",
    body: formData,
    signal,
  });

  if (!response.ok) {
    let errorDetail = "Execution gateway processing exception.";
    try {
      const errJson = await response.json();
      errorDetail = errJson.error || errJson.details || errorDetail;
    } catch {
      errorDetail = `Gateway returned status ${response.status}: ${response.statusText}`;
    }
    throw new Error(errorDetail);
  }

  return await response.json();
}
