use pyo3::prelude::*;
mod engine;
pub mod filters;
mod types;

#[pymodule]
fn url_reputation_rust(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<engine::URLReputationPlugin>()?;
    Ok(())
}
