from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import os
from main import find_models_by_name_parts, expand_providers, _load_search_terms
import csv
from typing import List, Dict, Any

app = FastAPI(title="OpenRouter Models API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "OpenRouter Models API"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.post("/refresh-data")
async def refresh_data():
    """Refresh the model data by fetching from OpenRouter API"""
    try:
        search_terms = _load_search_terms()
        models = find_models_by_name_parts(search_terms)
        rows = expand_providers(models)

        # Write to CSV in frontend public directory
        output_dir = "frontend/public"
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, "openrouter_models_providers.csv")

        with open(output_path, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(
                [
                    "Model name",
                    "Model URL",
                    "OpenRouter model ID",
                    "Provider",
                    "Context length",
                    "Price/input token",
                    "Price/output token",
                    "Latency",
                    "Throughput",
                ]
            )
            for r in rows:
                w.writerow(
                    [
                        r.model_name,
                        r.model_url,
                        r.model_id,
                        r.provider,
                        r.context_length,
                        r.price_input_token,
                        r.price_output_token,
                        r.latency,
                        r.throughput,
                    ]
                )

        return {
            "message": "Data refreshed successfully",
            "models_found": len(models),
            "provider_rows": len(rows),
            "output_file": output_path,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error refreshing data: {str(e)}")


@app.get("/csv")
async def get_csv():
    """Serve the CSV file"""
    csv_path = "frontend/public/openrouter_models_providers.csv"
    if not os.path.exists(csv_path):
        raise HTTPException(
            status_code=404, detail="CSV file not found. Run /refresh-data first."
        )

    return FileResponse(
        path=csv_path, media_type="text/csv", filename="openrouter_models_providers.csv"
    )


@app.get("/models")
async def get_models():
    """Get models data as JSON"""
    try:
        search_terms = _load_search_terms()
        models = find_models_by_name_parts(search_terms)
        rows = expand_providers(models)

        # Group by author and model
        authors: Dict[str, Dict[str, List[Dict[str, Any]]]] = {}

        for row in rows:
            author_name = (
                row.model_name.split(":")[0]
                if ":" in row.model_name
                else row.model_name.split("/")[0]
            )
            model_name = row.model_name

            if author_name not in authors:
                authors[author_name] = {}
            if model_name not in authors[author_name]:
                authors[author_name][model_name] = []

            authors[author_name][model_name].append(
                {
                    "Model name": row.model_name,
                    "Model URL": row.model_url,
                    "OpenRouter model ID": row.model_id,
                    "Provider": row.provider,
                    "Context length": str(row.context_length)
                    if row.context_length
                    else "",
                    "Price/input token": str(row.price_input_token)
                    if row.price_input_token
                    else "",
                    "Price/output token": str(row.price_output_token)
                    if row.price_output_token
                    else "",
                    "Latency": str(row.latency) if row.latency else "",
                    "Throughput": str(row.throughput) if row.throughput else "",
                }
            )

        # Convert to the expected format
        result = []
        for author_name, models_dict in authors.items():
            author_models = []
            for model_name, providers in models_dict.items():
                author_models.append(
                    {
                        "name": model_name,
                        "url": providers[0]["Model URL"],
                        "id": providers[0]["OpenRouter model ID"],
                        "providers": providers,
                    }
                )

            result.append({"name": author_name, "models": author_models})

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching models: {str(e)}")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
