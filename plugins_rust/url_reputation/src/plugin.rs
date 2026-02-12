use pyo3::prelude::*;
use std::collections::HashMap;
use url::Url;

#[derive(Debug, Clone)]
pub struct URLReputationPluginConfig {
    name: String,
    kind: String,
    hooks: Vec<String>,
    config: HashMap<String, Vec<String>>,
}

#[derive(Debug, Clone)]
pub struct PluginViolation {
    reason: String,
    description: String,
    code: String,
    details: String,
}

#[derive(Debug, Clone)]
pub struct ResourcePreFetchResult {
    continue_processing: bool,
    violation: Option<PluginViolation>,
}

#[pyclass]
pub struct URLReputationPlugin {
    config: URLReputationPluginConfig,
}

impl URLReputationPlugin {
    pub fn new(config: URLReputationPluginConfig) -> Self {
        Self { config }
    }

    #[pymethods]
    pub fn resource_pre_fetch(payload: Py<PyAny>) -> PyResult<ResourcePreFetchResult> {
        // Check URL against blocked domains and patterns before fetch.
        //  Args:
        //      payload: Resource pre-fetch payload.
        //      context: Plugin execution context.
        //  Returns:
        //      Result indicating whether URL is allowed or blocked.
        let blocked_domains: Vec<String> = [];
        let blocked_patterns: Vec<String> = [];

        let parsed =
            Url::parse(payload.url).with_context(|| format!("Could not parse url: {}", url));
        let hostname = parsed
            .host_str()
            .with_context(|| format!("Could not parse url hostname {}", url));

        // domain check
        for domain in blocked_domains {
            if hostname.endswith(domain) | hostname == domain {
                return ResourcePreFetchResult::new(
                    False,
                    PluginViolation(
                        "Blocked domain".to_string(),
                        format!("Domain {} is blocked", hostname),
                        "URL_REPUTATION_BLOCK".to_string(),
                        format!("{{\"domain\": {}}}", hostname),
                    ),
                );
            }
        }
        // pattern check
        url = payload.url;
        for pattern in blocked_patterns {
            if url.contains(pattern) | url == pattern {
                return ResourcePreFetchResult(
                    False,
                    PluginViolation(
                        "Blocked pattern".to_string(),
                        format!("URL matches blocked pattern: {}", pattern),
                        "URL_REPUTATION_BLOCK".to_string(),
                        format!("{{\"pattern\": {}}}", pattern),
                    ),
                );
            }
        }

        Ok(ResourcePreFetchResult {
            continue_processing: True,
            violation: None,
        })
    }
}
