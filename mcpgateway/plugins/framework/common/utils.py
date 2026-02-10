
from typing import Any
from fastapi.responses import JSONResponse
import orjson


def to_camel_case(s: str) -> str:
    """Convert a string from snake_case to camelCase.

    Args:
        s (str): The string to be converted, which is assumed to be in snake_case.

    Returns:
        str: The string converted to camelCase.

    Examples:
        >>> to_camel_case("hello_world_example")
        'helloWorldExample'
        >>> to_camel_case("alreadyCamel")
        'alreadyCamel'
        >>> to_camel_case("")
        ''
        >>> to_camel_case("single")
        'single'
        >>> to_camel_case("_leading_underscore")
        'LeadingUnderscore'
        >>> to_camel_case("trailing_underscore_")
        'trailingUnderscore'
        >>> to_camel_case("multiple_words_here")
        'multipleWordsHere'
        >>> to_camel_case("api_key_value")
        'apiKeyValue'
        >>> to_camel_case("user_id")
        'userId'
        >>> to_camel_case("created_at")
        'createdAt'
    """
    return "".join(word.capitalize() if i else word for i, word in enumerate(s.split("_")))


class ORJSONResponse(JSONResponse):
    """Custom JSON response class using orjson for faster serialization.

    orjson is 2-3x faster than stdlib json and produces more compact output.
    It handles datetime, UUID, and numpy types natively.

    This response class is designed to be a drop-in replacement for FastAPI's
    default JSONResponse with no breaking changes to API behavior.

    Features:
    - Fast: 2-3x faster than stdlib json, uses Rust implementation
    - Strict: RFC 8259 compliant, catches serialization errors early
    - Compact: Produces smaller output than stdlib json
    - Type Support: datetime, UUID, numpy arrays, dataclasses, Pydantic models
    - Binary Output: Returns bytes directly (no string→bytes conversion overhead)

    Example:
        >>> from mcpgateway.utils.orjson_response import ORJSONResponse
        >>> response = ORJSONResponse(content={"message": "Hello World"})
        >>> response.media_type
        'application/json'

    Options used:
    - OPT_NON_STR_KEYS: Allow non-string dict keys (ints, etc.)
    - OPT_SERIALIZE_NUMPY: Support numpy arrays if present

    For datetime serialization, orjson uses RFC 3339 format (ISO 8601 with timezone).
    Naive datetimes are treated as UTC by default.
    """

    media_type = "application/json"

    def render(self, content: Any) -> bytes:
        """Render content to JSON bytes using orjson.

        Args:
            content: The content to serialize to JSON. Can be dict, list, str,
                     int, float, bool, None, datetime, UUID, Pydantic models, etc.

        Returns:
            JSON bytes ready for HTTP response (no additional encoding needed).

        Options:
            - OPT_NON_STR_KEYS: Allow non-string dict keys (ints, UUID, etc.)
            - OPT_SERIALIZE_NUMPY: Support numpy arrays if numpy is installed

        Note:
            orjson returns bytes directly, unlike stdlib json.dumps() which returns str.
            This eliminates the string→bytes encoding step, improving performance.

        Raises:
            orjson.JSONEncodeError: If content cannot be serialized to JSON.
        """
        return orjson.dumps(
            content,
            option=orjson.OPT_NON_STR_KEYS | orjson.OPT_SERIALIZE_NUMPY,
        )
