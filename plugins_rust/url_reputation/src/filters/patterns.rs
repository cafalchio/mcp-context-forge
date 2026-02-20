use regex::Regex;

pub fn in_blocked_patterns_regex(domain: &str, blocked_patterns: &[Regex]) -> bool {
    blocked_patterns.iter().any(|re| re.is_match(domain))
}

pub fn in_allow_patterns_regex(domain: &str, allowed_pattens: &[Regex]) -> bool {
    allowed_pattens.iter().any(|re| re.is_match(domain))
}

pub fn in_domain_list(domain: &str, check_domains: &Vec<String>) -> bool {
    for check_domain in check_domains {
        if domain == check_domain || domain.ends_with(&format!(".{}", check_domain)) {
            return true;
        }
    }
    false
}
