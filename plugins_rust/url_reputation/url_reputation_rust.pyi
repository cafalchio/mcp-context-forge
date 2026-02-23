from typing import Optional, Dict, Set, List

class URLReputationConfig:
    """
    Configuration for URL reputation checking.

    Attributes:
        whitelist_domains: Set of domains that are always allowed
        allowed_patterns: List of regex patterns for allowed URLs
        blocked_domains: Set of domains that are always blocked
        blocked_patterns: List of regex patterns for blocked URLs
        use_heuristic_check: Enable heuristic checks (entropy, suspicious patterns)
        entropy_threshold: Threshold for entropy-based detection (default: 3.5)
        block_non_secure_http: Block non-HTTPS URLs
    """
    whitelist_domains: Set[str]
    allowed_patterns: List[str]
    blocked_domains: Set[str]
    blocked_patterns: List[str]
    use_heuristic_check: bool
    entropy_threshold: float
    block_non_secure_http: bool

    def __init__(
        self,
        whitelist_domains: Set[str],
        allowed_patterns: List[str],
        blocked_domains: Set[str],
        blocked_patterns: List[str],
        use_heuristic_check: bool,
        entropy_threshold: float,
        block_non_secure_http: bool,
    ) -> None: ...

class PluginViolation:
    """
    Represents a policy violation detected by the plugin.

    Attributes:
        reason: Short reason for the violation
        description: Detailed description of the violation
        code: Error code identifying the violation type
        details: Optional additional details about the violation
    """
    reason: str
    description: str
    code: str
    details: Optional[Dict[str, str]]

    def __init__(
        self,
        reason: str,
        description: str,
        code: str,
        details: Optional[Dict[str, str]] = None,
    ) -> None: ...

class URLPluginResult:
    """
    Result of URL validation.

    Attributes:
        continue_processing: Whether to continue processing the URL
        violation: Optional violation information if URL was blocked
    """
    continue_processing: bool
    violation: Optional[PluginViolation]

    def __init__(
        self,
        continue_processing: bool,
        violation: Optional[PluginViolation] = None,
    ) -> None: ...

class URLReputationPlugin:
    """
    URLReputationPlugin evaluates URLs against a configurable reputation policy.

    Checks include:
    - Whitelist/blocklist domain matching
    - Pattern-based URL filtering
    - Heuristic analysis (entropy, suspicious patterns)
    - HTTP/HTTPS enforcement
    """

    def __init__(self, config: URLReputationConfig) -> None:
        """
        Initialize the URLReputationPlugin with a configuration.

        Args:
            config: URLReputationConfig object containing whitelist, blocked patterns, etc.
        """
        ...

    def validate_url(self, url: str) -> URLPluginResult:
        """
        Validate a URL against the plugin's rules.

        Args:
            url: The URL to evaluate.

        Returns:
            URLPluginResult: Contains `continue_processing` flag and optional violation info.
        """
        ...
