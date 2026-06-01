from uuid import UUID

from llama_index.core.schema import NodeWithScore

from rag.config import Config
from rag.query.types import SourceRef


def is_image_node(node_with_score: NodeWithScore) -> bool:
    return (
        node_with_score.node.metadata.get("content_kind") == Config.CONTENT_KIND_IMAGE
    )


def _parse_source_ref(node_with_score: NodeWithScore) -> SourceRef | None:
    metadata = node_with_score.node.metadata
    chunk_id = metadata.get("chunk_id")
    document_id = metadata.get("document_id")
    if not chunk_id or not document_id:
        return None
    try:
        parsed_document_id = UUID(document_id)
        parsed_chunk_id = UUID(chunk_id)
    except ValueError:
        return None

    quoted = node_with_score.node.get_content()
    content_kind = metadata.get("content_kind")
    return SourceRef(
        document_id=parsed_document_id,
        chunk_id=parsed_chunk_id,
        score=node_with_score.score,
        quoted_text=quoted[:2000] if quoted else None,
        content_kind=str(content_kind) if content_kind else None,
        s3_key=metadata.get("s3_key"),
        filename=metadata.get("filename"),
        mime_type=metadata.get("mime_type"),
    )


def sources_from_nodes(nodes: list[NodeWithScore]) -> list[SourceRef]:
    sources: list[SourceRef] = []
    seen_chunk_ids: set[str] = set()
    for node_with_score in nodes:
        metadata = node_with_score.node.metadata
        chunk_id = metadata.get("chunk_id")
        if not chunk_id or chunk_id in seen_chunk_ids:
            continue
        source_ref = _parse_source_ref(node_with_score)
        if source_ref is None:
            continue
        seen_chunk_ids.add(chunk_id)
        sources.append(source_ref)
    return sources
