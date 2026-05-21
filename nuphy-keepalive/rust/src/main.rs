use glob::glob;
use std::fs::{File, OpenOptions};
use std::io::{Read, Write};
use std::path::PathBuf;
use std::thread;
use std::time::Duration;

// NuPhy Air75 HE IDs (uevent format)
const VENDOR_ID: &str = "000019F5";
const PRODUCT_ID: &str = "00006120";

// The working Keep-Alive Packet from the Nuphy drive website
const PACKET: [u8; 64] = [
    0x55, 0x03, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
];

fn find_nuphy_device() -> Option<PathBuf> {
    let target_str = format!("HID_ID=0003:{}:{}", VENDOR_ID, PRODUCT_ID);
    let mut found_devices: Vec<PathBuf> = Vec::new();

    let paths = glob("/sys/class/hidraw/hidraw*").expect("Failed to read glob pattern");


    // scan sys for corrrect nuphy hidraw and translate to dev path.
    for entry in paths {
        if let Ok(path) = entry {
            let uevent_path = path.join("device/uevent");

            if let Ok(mut file) = File::open(&uevent_path) {
                let mut contents = String::new();
                if file.read_to_string(&mut contents).is_ok() {
                    if contents.contains(&target_str) {
                        if let Some(name) = path.file_name() {
                            let dev_path = PathBuf::from("/dev").join(name);
                            found_devices.push(dev_path);
                        }
                    }
                }
            }
        }
    }

    if found_devices.is_empty() {
        return None;
    }

    found_devices.sort();

    println!("Found interfaces: {:?}", found_devices);

    // Pick the middle interface which is the vendor interface, hopefully always?
    let selected = if found_devices.len() >= 2 {
        &found_devices[1]
    } else {
        &found_devices[0]
    };

    println!("Selecting interface: {:?}", selected);
    Some(selected.clone())
}

fn main() {
    println!("Starting NuPhy Keep-Alive Daemon (Rust)");

    // Reconnection logic
    loop {
        match find_nuphy_device() {
            Some(dev_path) => {
                println!("Opening device: {:?}", dev_path);

                // Open device for writing
                match OpenOptions::new().write(true).read(true).open(&dev_path) {
                    Ok(mut file) => {
                        println!("Connected. Starting heartbeat loop...");

                        // Connected, keepalive logic
                        loop {
                            match file.write_all(&PACKET) {
                                Ok(_) => {
                                    println!("Heartbeat sent.");
                                    thread::sleep(Duration::from_secs(60));
                                }
                                Err(e) => {
                                    eprintln!("Write failed (Device disconnected?): {}", e);
                                    break; // back to rescan loop
                                }
                            }
                        }
                    }
                    Err(e) => {
                        eprintln!("Failed to open device {:?}: {}", dev_path, e);
                    }
                }
            }
            None => {
                eprintln!("NuPhy keyboard not found. Retrying in 15s...");
            }
        }

        thread::sleep(Duration::from_secs(15));
    }
}