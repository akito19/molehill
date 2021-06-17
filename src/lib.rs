// File generation
pub mod default_template;
pub mod template;

pub fn unless(cond: bool) -> bool {
    if cond {
        false
    } else {
        true
    }
}
