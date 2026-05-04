// Learn more about Tauri commands at https://tauri.app/develop/calling-rust/

use std::path::PathBuf;
use std::process::Child;
use std::sync::Mutex;
use tauri::utils::platform::current_exe;
use tauri::{App, RunEvent};

static PYTHON_PROCESS: Mutex<Option<Child>> = Mutex::new(None);
static NODE_PROCESS: Mutex<Option<Child>> = Mutex::new(None);

#[tauri::command]
fn greet(name: &str) -> String {
    format!("Hello, {}! You've been greeted from Rust!", name)
}

fn is_app_mode() -> bool {
    current_exe()
        .unwrap()
        .to_string_lossy()
        .contains("Contents/MacOS")
}

/// 获取 macOS 应用内的 Resources/_up_ 资源目录
fn get_resource_dir() -> Result<PathBuf, &'static str> {
    // 1. 获取当前可执行文件路径
    let exe_path = current_exe().map_err(|_| "无法获取可执行文件路径")?;

    // 2. 获取可执行文件所在目录：xxx.app/Contents/MacOS
    let exe_dir = exe_path.parent().ok_or("无法获取可执行文件目录")?;
    if exe_path.to_string_lossy().contains("Contents/MacOS") {
        // 3. 向上跳一级到 Contents，再进入 Resources/_up_
        let resource_dir = exe_dir
            .parent()
            .ok_or("无法跳转到 Contents 目录")?
            .join("Resources")
            .join("_up_");

        Ok(resource_dir.to_path_buf())
    } else {
        let resource_dir = exe_dir.join("_up_");
        Ok(resource_dir.to_path_buf())
    }
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    let app = tauri::Builder::default()
        .plugin(tauri_plugin_opener::init())
        .invoke_handler(tauri::generate_handler![greet])
        .setup(|_app: &mut App| {
            let resource_dir: PathBuf = get_resource_dir().map_err(|_| "无法获取资源目录")?;
            println!("资源目录: {:?}", resource_dir);

            let python_script: PathBuf = resource_dir.join("src-python/mxdict-server.py");
            println!("Python 脚本路径: {:?}", python_script);
            // let dist_dir: PathBuf = resource_dir.join("dist");

            // 启动 Python
            let python_child = std::process::Command::new("python3.11")
                .arg(python_script)
                .spawn()
                .map_err(|e| format!("启动 Python 失败: {}", e))?;

            *PYTHON_PROCESS.lock().unwrap() = Some(python_child);

            if is_app_mode() {
                let dist_dir: PathBuf = resource_dir.join("dist");
                let node_child = std::process::Command::new("npx")
                    .arg("vite")
                    .arg("preview")
                    .arg("--port")
                    .arg("9595")
                    .arg("--strictPort")
                    .arg("--outDir")
                    .arg(dist_dir)
                    .spawn()
                    .map_err(|e| format!("启动 Node 失败: {}", e))?;
                *NODE_PROCESS.lock().unwrap() = Some(node_child);
            }
            Ok(())
        })
        .build(tauri::generate_context!())
        .expect("error while building tauri application");

    app.run(|_, event: RunEvent| {
        if let RunEvent::Exit = event {
            if let Some(mut proc) = PYTHON_PROCESS.lock().unwrap().take() {
                let _ = proc.kill();
                let _ = proc.wait();
                println!("🛑 Python 服务器已关闭");
            }
            if let Some(mut proc) = NODE_PROCESS.lock().unwrap().take() {
                let _ = proc.kill();
                let _ = proc.wait();
                println!("🛑 Node 服务器已关闭");
            }
        }
    });
}
