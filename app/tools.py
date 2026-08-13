# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import math
import os
import uuid

SERVERLESS_RAG_CORPUS_NAME = "projects/336327133324/locations/us-central1/ragCorpora/1265836950732931072"

# HARDCODED PROJECT ID as string literal (required for Vertex AI Agent Platform)
FIRESTORE_PROJECT_ID = "qwiklabs-gcp-03-59f89a78fde9"
STATIC_ASSETS_BUCKET = "qwiklabs-gcp-03-59f89a78fde9-static-assets-bucket"
from typing import Any


def calculate(expression: str) -> str:
    """Evaluates a mathematical expression safely.

    Args:
        expression: A mathematical expression string, e.g. "2 + 3 * 4" or "math.sqrt(16) + math.sin(math.pi / 2)".

    Returns:
        The result of evaluating the mathematical expression as a string.
    """
    try:
        # Safe evaluation namespace limited to math module
        allowed_names = {k: v for k, v in math.__dict__.items() if not k.startswith("__")}
        allowed_names.update({"abs": abs, "round": round, "min": min, "max": max, "pow": pow})
        result = eval(expression, {"__builtins__": None}, allowed_names)
        return f"Result: {result}"
    except Exception as e:
        return f"Error evaluating expression '{expression}': {e}"


def convert_units(value: float, from_unit: str, to_unit: str) -> str:
    """Converts a numerical value from one unit of measurement to another.

    Supported unit categories:
    - Length: m, km, cm, mm, ft, miles, inches
    - Weight: kg, g, lbs, oz
    - Temperature: celsius (C), fahrenheit (F), kelvin (K)

    Args:
        value: The numerical value to convert.
        from_unit: The unit to convert from (e.g., "km", "miles", "celsius", "kg", "lbs").
        to_unit: The unit to convert to (e.g., "m", "feet", "fahrenheit", "lbs").

    Returns:
        A string describing the conversion result.
    """
    fu = from_unit.lower().strip()
    tu = to_unit.lower().strip()

    # Temperature conversion
    temp_units = {"c", "celsius", "f", "fahrenheit", "k", "kelvin"}
    if fu in temp_units or tu in temp_units:
        # Convert from_unit to Celsius first
        if fu in ("c", "celsius"):
            c_val = value
        elif fu in ("f", "fahrenheit"):
            c_val = (value - 32) * 5 / 9
        elif fu in ("k", "kelvin"):
            c_val = value - 273.15
        else:
            return f"Unsupported temperature unit: {from_unit}"

        # Convert Celsius to to_unit
        if tu in ("c", "celsius"):
            res = c_val
        elif tu in ("f", "fahrenheit"):
            res = (c_val * 9 / 5) + 32
        elif tu in ("k", "kelvin"):
            res = c_val + 273.15
        else:
            return f"Unsupported temperature unit: {to_unit}"

        return f"{value} {from_unit} = {res:.4f} {to_unit}"

    # Length conversion (base unit: meters)
    length_to_m = {
        "m": 1.0, "meter": 1.0, "meters": 1.0,
        "km": 1000.0, "kilometer": 1000.0, "kilometers": 1000.0,
        "cm": 0.01, "centimeter": 0.01, "centimeters": 0.01,
        "mm": 0.001, "millimeter": 0.001, "millimeters": 0.001,
        "ft": 0.3048, "feet": 0.3048, "foot": 0.3048,
        "inch": 0.0254, "inches": 0.0254, "in": 0.0254,
        "mile": 1609.344, "miles": 1609.344
    }

    if fu in length_to_m and tu in length_to_m:
        m_val = value * length_to_m[fu]
        res = m_val / length_to_m[tu]
        return f"{value} {from_unit} = {res:.4f} {to_unit}"

    # Weight conversion (base unit: grams)
    weight_to_g = {
        "g": 1.0, "gram": 1.0, "grams": 1.0,
        "kg": 1000.0, "kilogram": 1000.0, "kilograms": 1000.0,
        "mg": 0.001, "milligram": 0.001, "milligrams": 0.001,
        "lb": 453.59237, "lbs": 453.59237, "pound": 453.59237, "pounds": 453.59237,
        "oz": 28.349523125, "ounce": 28.349523125, "ounces": 28.349523125
    }

    if fu in weight_to_g and tu in weight_to_g:
        g_val = value * weight_to_g[fu]
        res = g_val / weight_to_g[tu]
        return f"{value} {from_unit} = {res:.4f} {to_unit}"

    return f"Cannot convert from '{from_unit}' to '{to_unit}'. Please check supported units."


def consult_irs_docs(query: str) -> str:
    """Queries the official tax documentation and project brief corpus (Forms 1065, 1120, 1120-S instructions, and project brief) for rules, explanations, persona guidelines, and curriculum details.

    Args:
        query: What to look up in the corpus (e.g. "Form 1120 Schedule M-1 rules", "Form 1120-S AAA account", "Professor Teena persona voice rules").

    Returns:
        Relevant passages from the grounding corpus, or a message indicating no passages found.
    """
    import vertexai
    from vertexai.preview import rag

    try:
        project_id = os.environ.get("GOOGLE_CLOUD_PROJECT", "qwiklabs-gcp-03-59f89a78fde9")
        vertexai.init(project=project_id, location="us-central1")
        resp = rag.retrieval_query(
            text=query,
            rag_resources=[rag.RagResource(rag_corpus=SERVERLESS_RAG_CORPUS_NAME)],
            rag_retrieval_config=rag.RagRetrievalConfig(top_k=5),
        )
        contexts = getattr(resp.contexts, "contexts", [])
        passages = [c.text.strip() for c in contexts if getattr(c, "text", "").strip()]
        return "\n\n---\n\n".join(passages) or "No relevant passage found in official grounding documentation."
    except Exception as e:
        return f"Error retrieving documentation: {e}"


def get_tax_case_studies(form_type: str = "") -> str:
    """Retrieves tax case studies from the Firestore database for practice, teaching, or student scenario review.

    Args:
        form_type: Optional filter by IRS form type, e.g. "1065", "1120", or "1120-S". Pass empty string "" for all forms.

    Returns:
        A formatted list of matching tax case studies including scenario descriptions, key questions, and solution keys.
    """
    from google.cloud import firestore
    from google.cloud.firestore_v1.base_query import FieldFilter

    try:
        db = firestore.Client(project=FIRESTORE_PROJECT_ID)
        col_ref = db.collection("tax_case_studies")

        if form_type and form_type.strip():
            clean_form = form_type.strip().upper().replace("FORM ", "").replace("FORM", "")
            docs = col_ref.where(filter=FieldFilter("form_type", "==", clean_form)).stream()
        else:
            docs = col_ref.stream()

        results = []
        for doc in docs:
            d = doc.to_dict()
            results.append(
                f"### Case Study ID: {d.get('id', doc.id)} | Title: {d.get('title')}\n"
                f"- **Form Type:** Form {d.get('form_type')} | **Difficulty:** {d.get('difficulty')} | **Topic:** {d.get('topic')}\n"
                f"- **Scenario Description:** {d.get('scenario_description')}\n"
                f"- **Key Question:** {d.get('key_question')}\n"
                f"- **Solution Key:** {d.get('solution_key')}\n"
            )

        if not results:
            return f"No tax case studies found in Firestore database for form type '{form_type}'."
        return "\n---\n".join(results)
    except Exception as e:
        return f"Error retrieving case studies from Firestore: {e}"


def save_tax_case_study(
    title: str,
    form_type: str,
    difficulty: str,
    topic: str,
    scenario_description: str,
    key_question: str,
    solution_key: str,
) -> str:
    """Saves a new custom tax case study scenario into the Firestore database for future student practice.

    Args:
        title: Short title for the case study (e.g., "Schedule K-1 Special Allocation").
        form_type: IRS form type ("1065", "1120", or "1120-S").
        difficulty: Difficulty level ("beginner", "intermediate", "advanced").
        topic: Tax topic covered (e.g. "AAA Sourcing", "Guaranteed Payments", "Section 179").
        scenario_description: Detailed fact pattern with taxpayer facts and numbers.
        key_question: The question or calculation for the student.
        solution_key: Line-by-line solution breakdown and IRS citations.

    Returns:
        A confirmation message with the saved Firestore document ID.
    """
    from google.cloud import firestore

    try:
        db = firestore.Client(project=FIRESTORE_PROJECT_ID)
        clean_form = form_type.strip().upper().replace("FORM ", "").replace("FORM", "")
        doc_id = f"cs_{clean_form.lower().replace('-', '')}_{uuid.uuid4().hex[:6]}"

        data = {
            "id": doc_id,
            "title": title.strip(),
            "form_type": clean_form,
            "difficulty": difficulty.strip().lower(),
            "topic": topic.strip(),
            "scenario_description": scenario_description.strip(),
            "key_question": key_question.strip(),
            "solution_key": solution_key.strip(),
        }

        db.collection("tax_case_studies").document(doc_id).set(data)
        return f"Successfully saved new tax case study '{title}' (ID: {doc_id}) into Firestore database!"
    except Exception as e:
        return f"Error saving tax case study to Firestore: {e}"


async def generate_domain_video(
    prompt: str,
    tool_context: Any = None,
) -> str:
    """Generates a short educational motion graphic or video for a corporate tax topic (e.g. Schedule K-1 allocations, Form 1120-S AAA, M-1 reconciliation) using Google Gemini Omni (gemini-omni-flash-preview) model in the global region.

    Saves the video as an artifact for the Playground and uploads it to the public Cloud Storage bucket.

    Args:
        prompt: Description of the tax video/graphic to generate (e.g., "A short animated video explaining Form 1065 Schedule K-1 partnership tax allocation").
        tool_context: ADK ToolContext injected by the framework at runtime.

    Returns:
        The public Cloud Storage URL (https://storage.googleapis.com/<bucket>/<object>) of the generated MP4 video.
    """
    import uuid
    from google import genai
    from google.genai import types
    from google.cloud import storage

    try:
        # 1. Call gemini-omni-flash-preview model via Vertex AI in global region
        client = genai.Client(
            vertexai=True,
            project=FIRESTORE_PROJECT_ID,
            location="global",
        )

        res = client.interactions.create(
            model="gemini-omni-flash-preview",
            input=prompt,
            generation_config={"response_modalities": ["VIDEO"]},
        )

        video_bytes = None
        if hasattr(res, "output_video") and res.output_video and getattr(res.output_video, "data", None):
            video_bytes = res.output_video.data
        elif hasattr(res, "outputs") and res.outputs:
            for out in res.outputs:
                if getattr(out, "mime_type", "") == "video/mp4" and getattr(out, "data", None):
                    video_bytes = out.data
                    break

        if not video_bytes:
            return f"Error: No video bytes returned from gemini-omni-flash-preview for prompt '{prompt}'."

        filename = f"tax_video_{uuid.uuid4().hex[:8]}.mp4"

        # 2. Save artifact using tool_context.save_artifact
        if tool_context and hasattr(tool_context, "save_artifact"):
            try:
                artifact_part = types.Part.from_bytes(data=video_bytes, mime_type="video/mp4")
                await tool_context.save_artifact(filename=filename, artifact=artifact_part)
            except Exception as artifact_err:
                print(f"Warning: Failed to save video artifact in tool_context: {artifact_err}")

        # 3. Upload video bytes to public Cloud Storage bucket
        storage_client = storage.Client(project=FIRESTORE_PROJECT_ID)
        bucket = storage_client.bucket(STATIC_ASSETS_BUCKET)
        blob_name = f"videos/{filename}"
        blob = bucket.blob(blob_name)
        blob.upload_from_string(video_bytes, content_type="video/mp4")

        public_url = f"https://storage.googleapis.com/{STATIC_ASSETS_BUCKET}/{blob_name}"
        return f"Successfully generated video! Public Cloud Storage URL: {public_url}"

    except Exception as e:
        return f"Error generating video with gemini-omni-flash-preview: {e}"
