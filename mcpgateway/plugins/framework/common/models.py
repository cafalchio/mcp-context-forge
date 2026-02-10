from enum import Enum
from typing import Any, Dict, List, Literal, Optional, Union
from pydantic import BaseModel, ConfigDict, Field
from mcpgateway.utils.base_models import BaseModelWithConfigDict


class Role(str, Enum):
    """Message role in conversations.

    Attributes:
        ASSISTANT (str): Indicates the assistant's role.
        USER (str): Indicates the user's role.

    Examples:
        >>> Role.USER.value
        'user'
        >>> Role.ASSISTANT.value
        'assistant'
        >>> Role.USER == 'user'
        True
        >>> list(Role)
        [<Role.ASSISTANT: 'assistant'>, <Role.USER: 'user'>]
    """

    ASSISTANT = "assistant"
    USER = "user"


# MCP Protocol Annotations
class Annotations(BaseModel):
    """Optional annotations for client rendering hints (MCP spec-compliant).

    Attributes:
        audience (Optional[List[Role]]): Describes who the intended customer of this
                                        object or data is. Can include multiple entries
                                        (e.g., ["user", "assistant"]).
        priority (Optional[float]): Describes how important this data is for operating
                                   the server. 1 = most important (effectively required),
                                   0 = least important (entirely optional).
        last_modified (Optional[str]): ISO 8601 timestamp of last modification.
                                      Serialized as 'lastModified' in JSON.
    """

    audience: Optional[List[Role]] = None
    priority: Optional[float] = Field(None, ge=0, le=1)
    last_modified: Optional[str] = Field(None, alias="lastModified")

    model_config = ConfigDict(populate_by_name=True)


# Base content types
class TextContent(BaseModelWithConfigDict):
    """Text content for messages (MCP spec-compliant).

    Attributes:
        type (Literal["text"]): The fixed content type identifier for text.
        text (str): The actual text message.
        annotations (Optional[Annotations]): Optional annotations for the client.
        meta (Optional[Dict[str, Any]]): Optional metadata for protocol extension.
                                        Serialized as '_meta' in JSON.

    Examples:
        >>> content = TextContent(type='text', text='Hello World')
        >>> content.text
        'Hello World'
        >>> content.type
        'text'
        >>> content.model_dump(exclude_none=True)
        {'type': 'text', 'text': 'Hello World'}
    """

    type: Literal["text"]
    text: str
    annotations: Optional[Annotations] = None
    meta: Optional[Dict[str, Any]] = Field(None, alias="_meta")


class ImageContent(BaseModelWithConfigDict):
    """Image content for messages (MCP spec-compliant).

    Attributes:
        type (Literal["image"]): The fixed content type identifier for images.
        data (str): Base64-encoded image data for JSON compatibility.
        mime_type (str): The MIME type (e.g. "image/png") of the image.
                        Will be serialized as 'mimeType' in JSON.
        annotations (Optional[Annotations]): Optional annotations for the client.
        meta (Optional[Dict[str, Any]]): Optional metadata for protocol extension.
                                        Serialized as '_meta' in JSON.
    """

    type: Literal["image"]
    data: str  # Base64-encoded string for JSON compatibility
    mime_type: str  # Will be converted to mimeType by alias_generator
    annotations: Optional[Annotations] = None
    meta: Optional[Dict[str, Any]] = Field(None, alias="_meta")


class LogLevel(str, Enum):
    """Standard syslog severity levels as defined in RFC 5424.

    Attributes:
        DEBUG (str): Debug level.
        INFO (str): Informational level.
        NOTICE (str): Notice level.
        WARNING (str): Warning level.
        ERROR (str): Error level.
        CRITICAL (str): Critical level.
        ALERT (str): Alert level.
        EMERGENCY (str): Emergency level.
    """

    DEBUG = "debug"
    INFO = "info"
    NOTICE = "notice"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"
    ALERT = "alert"
    EMERGENCY = "emergency"


class ToolAnnotations(BaseModel):
    """Tool behavior hints for clients (MCP spec-compliant).

    Attributes:
        title (Optional[str]): Human-readable display name for the tool.
        read_only_hint (Optional[bool]): If true, tool does not modify its environment.
        destructive_hint (Optional[bool]): If true, tool may perform destructive updates.
                                          Only meaningful when read_only_hint == false.
        idempotent_hint (Optional[bool]): If true, calling repeatedly with same arguments
                                         has no additional effect. Only meaningful when
                                         read_only_hint == false.
        open_world_hint (Optional[bool]): If true, tool may interact with an "open world"
                                         of external entities (e.g., web search).
    """

    title: Optional[str] = None
    read_only_hint: Optional[bool] = Field(None, alias="readOnlyHint")
    destructive_hint: Optional[bool] = Field(None, alias="destructiveHint")
    idempotent_hint: Optional[bool] = Field(None, alias="idempotentHint")
    open_world_hint: Optional[bool] = Field(None, alias="openWorldHint")

    model_config = ConfigDict(populate_by_name=True)


class AudioContent(BaseModelWithConfigDict):
    """Audio content for messages (MCP spec-compliant).

    Attributes:
        type (Literal["audio"]): The fixed content type identifier for audio.
        data (str): Base64-encoded audio data for JSON compatibility.
        mime_type (str): The MIME type of the audio (e.g., "audio/wav", "audio/mp3").
                        Different providers may support different audio types.
                        Will be serialized as 'mimeType' in JSON.
        annotations (Optional[Annotations]): Optional annotations for the client.
        meta (Optional[Dict[str, Any]]): Optional metadata for protocol extension.
                                        Serialized as '_meta' in JSON.
    """

    type: Literal["audio"]
    data: str  # Base64-encoded string for JSON compatibility
    mime_type: str  # Will be converted to mimeType by alias_generator
    annotations: Optional[Annotations] = None
    meta: Optional[Dict[str, Any]] = Field(None, alias="_meta")


# Legacy ResourceContent for backwards compatibility
class ResourceContent(BaseModel):
    """Resource content that can be embedded (LEGACY - use TextResourceContents or BlobResourceContents).

    This class is maintained for backwards compatibility but does not fully comply
    with the MCP spec. New code should use TextResourceContents or BlobResourceContents.

    Attributes:
        type (Literal["resource"]): The fixed content type identifier for resources.
        id (str): The ID identifying the resource.
        uri (str): The URI of the resource.
        mime_type (Optional[str]): The MIME type of the resource, if known.
        text (Optional[str]): A textual representation of the resource, if applicable.
        blob (Optional[bytes]): Binary data of the resource, if applicable.
    """

    type: Literal["resource"]
    id: str
    uri: str
    mime_type: Optional[str] = None
    text: Optional[str] = None
    blob: Optional[bytes] = None


class TransportType(str, Enum):
    """
    Enumeration of supported transport mechanisms for communication between components.

    Attributes:
        SSE (str): Server-Sent Events transport.
        HTTP (str): Standard HTTP-based transport.
        STDIO (str): Standard input/output transport.
        STREAMABLEHTTP (str): HTTP transport with streaming.
    """

    SSE = "SSE"
    HTTP = "HTTP"
    STDIO = "STDIO"
    STREAMABLEHTTP = "STREAMABLEHTTP"


ContentType = Union[TextContent, ImageContent, ResourceContent]

# Message types


class Message(BaseModel):
    """A message in a conversation.

    Attributes:
        role (Role): The role of the message sender.
        content (ContentType): The content of the message.
    """

    role: Role
    content: ContentType


class PromptResult(BaseModel):
    """Result of rendering a prompt template.

    Attributes:
        messages (List[Message]): The list of messages produced by rendering the prompt.
        description (Optional[str]): An optional description of the rendered result.
    """

    messages: List[Message]
    description: Optional[str] = None
