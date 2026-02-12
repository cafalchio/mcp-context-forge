use pyo3::prelude::*;

pub mod plugin;
use plugin::URLReputationPlugin;

/// URL Reputation plugin for blocking malicious domains and patterns
#[pymodule]
fn url_reputation(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<URLReputationPlugin>()?;
    Ok(())
}

