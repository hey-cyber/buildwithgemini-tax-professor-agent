import vertexai
from vertexai.preview import rag
from vertexai.preview.rag.utils import resources as rr

PROJECT_ID = "qwiklabs-gcp-03-59f89a78fde9"
LOCATION = "us-central1"

vertexai.init(project=PROJECT_ID, location=LOCATION)

# 1. Update RAG engine config to serverless mode
cfg = f"projects/{PROJECT_ID}/locations/{LOCATION}/ragEngineConfig"
print("Setting RAG Engine to serverless mode...")
rag.update_rag_engine_config(
    rag_engine_config=rag.RagEngineConfig(
        name=cfg,
        rag_managed_db_config=rag.RagManagedDbConfig(mode=rr.Serverless()),
    )
)

# 2. Create serverless RAG corpus
print("Creating serverless RAG corpus...")
corpus = rag.create_corpus(
    display_name="tax-professor-serverless-corpus",
    embedding_model_config=rag.EmbeddingModelConfig(
        publisher_model="publishers/google/models/text-embedding-005"
    ),
)
print(f"Created serverless corpus: {corpus.name}")

# 3. Import project_brief.md and IRS documents
GCS_PATHS = [
    "gs://qwiklabs-gcp-03-59f89a78fde9-rag-docs/project_brief.md",
    "gs://qwiklabs-gcp-03-59f89a78fde9-rag-docs/irs-documents/i1065-markdown.md",
    "gs://qwiklabs-gcp-03-59f89a78fde9-rag-docs/irs-documents/i1120-markdown.md",
    "gs://qwiklabs-gcp-03-59f89a78fde9-rag-docs/irs-documents/i1120s-markdown.md",
]

PARSING_PROMPT = (
    "Extract useful tax rules, line-item instructions, form guidance, "
    "and project brief persona details. Omit boilerplate."
)

print("Importing documents into serverless RAG corpus...")
resp = rag.import_files(
    corpus_name=corpus.name,
    paths=GCS_PATHS,
    transformation_config=rag.TransformationConfig(
        chunking_config=rag.ChunkingConfig(chunk_size=512, chunk_overlap=100)
    ),
    llm_parser=rag.LlmParserConfig(
        model_name="gemini-2.5-flash",
        custom_parsing_prompt=PARSING_PROMPT,
    ),
)

print(f"Import complete! Imported files count: {resp.imported_rag_files_count}")
print(f"SERVERLESS_RAG_CORPUS_NAME = \"{corpus.name}\"")
