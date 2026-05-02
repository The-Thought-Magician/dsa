pub struct Auth; impl Auth { pub fn verify(token: &str) -> bool { !token.is_empty() } }
