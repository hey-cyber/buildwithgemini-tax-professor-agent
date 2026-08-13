import os
import vertexai
from vertexai.preview import rag

PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT", "qwiklabs-gcp-03-59f89a78fde9")
LOCATION = "us-west1"
CORPUS_NAME = "projects/336327133324/locations/us-west1/ragCorpora/4611686018427387904"
GCS_PATH = "gs://qwiklabs-gcp-03-59f89a78fde9-rag-docs/irs-documents/"

print(f"Initializing Vertex AI RAG in {PROJECT_ID} ({LOCATION})...")
vertexai.init(project=PROJECT_ID, location=LOCATION)

print(f"Importing files from {GCS_PATH} into {CORPUS_NAME}...")
resp = rag.import_files(
    corpus_name=CORPUS_NAME,
    paths=[GCS_PATH],
    transformation_config=rag.TransformationConfig(
        chunking_config=rag.ChunkingConfig(chunk_size=512, chunk_overlap=100)
    ),
)
print("Successfully imported files count:", getattr(resp, "imported_rag_files_count", "done"))
