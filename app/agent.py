# ruff: noqa
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

from a2ui.basic_catalog.provider import BasicCatalog
from a2ui.schema.manager import A2uiSchemaManager
from google.adk.agents import Agent
from google.adk.agents.callback_context import CallbackContext
from google.adk.apps import App
from google.adk.models import Gemini
from google.adk.tools.preload_memory_tool import PreloadMemoryTool
from google.genai import types

from app.a2ui_utils import a2ui_callback
from app.tools import (
    calculate,
    consult_irs_docs,
    convert_units,
    generate_domain_video,
    get_tax_case_studies,
    save_tax_case_study,
)


MODEL = "gemini-3.6-flash"


# WRITE: after each turn, send the session to Memory Bank for extraction.
async def generate_memories_callback(callback_context: CallbackContext):
    await callback_context.add_session_to_memory()
    return None


schema_manager = A2uiSchemaManager(
    version="0.8",
    catalogs=[BasicCatalog.get_config("0.8")],
)

instruction = schema_manager.generate_system_prompt(
    role_description=(
        "You are a distinguished Senior CPA, Enrolled Agent, and Corporate Tax Professor with a Masters in Taxation (Professor Teena). "
        "You specialize in corporate tax returns (IRS Forms 1065, 1120, and 1120-S). "
        "Guide students patiently on each form, create custom case studies and scenarios, "
        "and answer basic to advanced corporate tax questions. "
        "When explaining specific line items, schedules, or tax rules on Forms 1065, 1120, or 1120-S, "
        "use the consult_irs_docs tool to search and reference official IRS instructions. "
        "You can look up existing practice case studies in the Firestore database using get_tax_case_studies, "
        "or save new custom case scenarios to the Firestore database using save_tax_case_study. "
        "FOR EVERY EXPLANATION (ESPECIALLY COMPLEX TAX TOPICS LIKE K-1 ALLOCATIONS, AAA ORDERING RULES, M-1 RECONCILIATIONS, AND BASIS TRACKING): "
        "Break down the answer into structured visual steps (e.g. [STEP 1], [STEP 2], [STEP 3], [SUMMARY]) in your response UI card. "
        "At the bottom of every step-by-step explanation card, ALWAYS include a visual option note inviting the student: "
        "'💡 VISUAL OPTION: Reply \"Visualize these steps in video\" or \"Generate video\" to produce an animated visual motion graphic.' "
        "When the student requests to 'visualize', 'show video', or 'generate video', immediately invoke the generate_domain_video tool. "
        "Remember student preferences, background, and previous topics discussed from memory."
    ),
    workflow_description="Analyze the request and return structured UI with visual step breakdowns.",
    ui_description=(
        "Always structure explanations into clear visual cards so students digest complex information easily: "
        "1. Title Text (usageHint: 'h1' or 'h2') with the form / tax topic name. "
        "2. Step-by-Step Breakdown using separate Text components prefixed with '[STEP 1]', '[STEP 2]', '[STEP 3]', and '[KEY FORMULA/RULE]'. "
        "3. Visual Option Callout at the bottom (usageHint: 'caption'): '💡 VISUAL OPTION: Reply \"Visualize these steps in video\" to generate an animated video diagram of this process.' "
        "Keep every surface clean and flat: ONE Card > ONE Column > a few Text rows. "
        "Never nest a Card inside a Card. "
        "Use ONLY these components: Card, Column, Row, Text, Divider, and Image. Do not use Table or Heading or Buttons. "
        "You may include one Image component, but only when you have a public https URL for the image. "
        "No markdown in text; use the usageHint property ('h1', 'h2', 'body', 'caption') for formatting. "
        "Output ONLY the raw A2UI JSON array — no prose, and never wrap it in <a2a_datapart_json> tags."
    ),
    include_schema=True,
    include_examples=True,
)


root_agent = Agent(
    name="root_agent",
    model=Gemini(
        model=MODEL,
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction=instruction,
    # READ: PreloadMemoryTool retrieves memories at the start of every turn and
    # injects them into the system instruction.
    tools=[
        calculate,
        convert_units,
        consult_irs_docs,
        get_tax_case_studies,
        save_tax_case_study,
        generate_domain_video,
        PreloadMemoryTool(),
    ],
    after_model_callback=a2ui_callback,
    after_agent_callback=generate_memories_callback,
)

app = App(
    root_agent=root_agent,
    name="app",
)
