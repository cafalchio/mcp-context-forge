use pyo3::prelude::*;
use pyo3::types::PyDict;
use std::collections::HashMap;
use url::Url;

#[derive(Debug, Clone)]
pub struct URLReputationPluginConfig {
    pub name: String,
    pub kind: String,
    pub hooks: Vec<String>,
    pub config: HashMap<String, Vec<String>>,
}

#[pyclass]
#[pyo3(from_py_object)]
#[derive(Debug, Clone)]
pub struct PluginViolation {
    #[pyo3(get)]
    pub reason: String,
    #[pyo3(get)]
    pub description: String,
    #[pyo3(get)]
    pub code: String,
    #[pyo3(get)]
    pub details: String,
}

#[pyclass]
#[derive(Debug)]
pub struct ResourcePreFetchResult {
    #[pyo3(get)]
    pub continue_processing: bool,
    #[pyo3(get)]
    pub violation: Option<Py<PluginViolation>>,
}

#[pyclass]
pub struct URLReputationPlugin {
    config: URLReputationPluginConfig,
}

#[pymethods]
impl URLReputationPlugin {
    #[new]
    pub fn new(config_dict: &Bound<'_, PyDict>) -> PyResult<Self> {
        // Extract configuration from Python dict
        let name: String = config_dict.get_item("name")?.ok_or_else(|| {
            PyErr::new::<pyo3::exceptions::PyKeyError, _>("Missing 'name' key")
        })?.extract()?;
        
        let kind: String = config_dict.get_item("kind")?.ok_or_else(|| {
            PyErr::new::<pyo3::exceptions::PyKeyError, _>("Missing 'kind' key")
        })?.extract()?;
        
        let hooks: Vec<String> = config_dict.get_item("hooks")?.ok_or_else(|| {
            PyErr::new::<pyo3::exceptions::PyKeyError, _>("Missing 'hooks' key")
        })?.extract()?;
        
        let config_data = config_dict.get_item("config")?.ok_or_else(|| {
            PyErr::new::<pyo3::exceptions::PyKeyError, _>("Missing 'config' key")
        })?;
        let config: HashMap<String, Vec<String>> = config_data.extract()?;
        
        let config = URLReputationPluginConfig {
            name,
            kind,
            hooks,
            config,
        };
        
        Ok(Self { config })
    }

    pub fn resource_pre_fetch(&self, py: Python<'_>, payload: Py<PyAny>) -> PyResult<Py<ResourcePreFetchResult>> {
        // Check URL against blocked domains and patterns before fetch.
        // Args:
        //     payload: Resource pre-fetch payload.
        // Returns:
        //     Result indicating whether URL is allowed or blocked.
        
        // Extract URL from payload using Bound API
        let payload_bound = payload.bind(py);
        let url_str: String = payload_bound.getattr("uri")?
            .extract::<String>()
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(
                format!("Could not extract uri from payload: {}", e)
            ))?;

        // Get blocked domains and patterns from config
        let blocked_domains: Vec<String> = self.config.config
            .get("blocked_domains")
            .cloned()
            .unwrap_or_default();

        let blocked_patterns: Vec<String> = self.config.config
            .get("blocked_patterns")
            .cloned()
            .unwrap_or_default();

        // Parse URL to get hostname
        let parsed = Url::parse(&url_str)
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(
                format!("Could not parse url: {}", e)
            ))?;

        let hostname = parsed.host_str()
            .ok_or_else(|| PyErr::new::<pyo3::exceptions::PyValueError, _>(
                format!("Could not parse url hostname from: {}", url_str)
            ))?;

        // Domain check
        for domain in &blocked_domains {
            if hostname == domain || hostname.ends_with(&format!(".{}", domain)) {
                let violation = PluginViolation {
                    reason: "Blocked domain".to_string(),
                    description: format!("Domain {} is blocked", hostname),
                    code: "URL_REPUTATION_BLOCK".to_string(),
                    details: format!(r#"{{"domain": "{}"}}"#, hostname),
                };
                let result = ResourcePreFetchResult {
                    continue_processing: false,
                    violation: Some(Py::new(py, violation)?),
                };
                return Ok(Py::new(py, result)?);
            }
        }

        // Pattern check
        for pattern in &blocked_patterns {
            if url_str.contains(pattern) || &url_str == pattern {
                let violation = PluginViolation {
                    reason: "Blocked pattern".to_string(),
                    description: format!("URL matches blocked pattern: {}", pattern),
                    code: "URL_REPUTATION_BLOCK".to_string(),
                    details: format!(r#"{{"pattern": "{}"}}"#, pattern),
                };
                let result = ResourcePreFetchResult {
                    continue_processing: false,
                    violation: Some(Py::new(py, violation)?),
                };
                return Ok(Py::new(py, result)?);
            }
        }

        // All checks passed
        let result = ResourcePreFetchResult {
            continue_processing: true,
            violation: None,
        };
        Ok(Py::new(py, result)?)
    }
}
