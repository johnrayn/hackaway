// recoverable error

use std::fs::File;
use std::io::ErrorKind;

fn basic() {
    let f = File::open("panics.rs");

    let f = match f {
        Ok(file) => file,
        Err(error) => {
            panic!("There was a problem opening the file: {:?}", error);
        },
    };
}

fn basic_improved() {
    let f = File::open("nonexistent.rs").expect("fail to open nonexistent.rs");
}

fn multi_error() {
    let f = File::open("multi_error.rs");

    let f = match f {
        Ok(file) => file,
        // note: ref refer a value and return a reference
        // & refer a reference and return a value
        Err(ref error) if error.kind() == ErrorKind::NotFound => {
            match File::create("multi_error.rs") {
                Ok(fc) => fc,
                Err(e) => {
                    panic!("Tried to create file but fail: {:?}", e);
                },
            }
        },
        Err(error) => {
            panic!("There was a problem opening the file {:?}", error);
        },
    };
}

use std::io;
use std::io::Read;

// progegating_error
fn read_username_from_file() -> Result<String, io::Error> {
    let f = File::open("hello.txt");
    
    let mut f = match f {
        Ok(file) => file,
        Err(e) => return Err(e),
    };

    let mut s = String::new();
    match f.read_to_string(&mut s) {
        Ok(_) => Ok(s),
        Err(e) => Err(e),
    }
}

fn progegating_error_improved() -> Result<String, io::Error> {
    let mut f = File::open("hello.txt")?;
    let mut s = String::new();
    f.read_to_string(&mut s)?;
    Ok(s)
}

fn main() {
    // basic();
    // basic_improved();
    // multi_error();
    let r = progegating_error_improved();
    println!("{:?}", r);
}