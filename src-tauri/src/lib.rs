// Learn more about Tauri commands at https://tauri.app/develop/calling-rust/

use chrono::Local;
use env_logger::{Builder, Env};
use log::{debug, error, info, warn};
use log::{Level, LevelFilter};
use std::fs::{self, OpenOptions};
use std::io::Write;
use std::path::PathBuf;
use std::process::Child;
use std::sync::Mutex;
use tauri::utils::platform::current_exe;
use tauri::{App, RunEvent};

/// 初始化日志：控制台彩色 + 文件输出 + 按天切割（Tauri 2.x 专用）
pub fn init_logging() {
    // 基础配置
    let env = Env::default().filter_or("RUST_LOG", "info");
    let mut builder = Builder::from_env(env);

    // 屏蔽第三方库噪音
    builder
        .filter_module("reqwest", LevelFilter::Warn)
        .filter_module("hyper", LevelFilter::Warn)
        .filter_module("hyper_util", LevelFilter::Warn)
        .filter_module("tauri_plugin_updater", LevelFilter::Warn);

    let exe_path = std::env::current_exe().unwrap();
    let exe_dir = exe_path.parent().expect("无法获取可执行文件目录");
    let log_dir = exe_dir.join("logs");
    println!("log_dir: {:?}", log_dir);
    let _ = fs::create_dir_all(&log_dir);

    // 自定义格式
    builder.format(move |buf, record| {
        let now = Local::now();
        let time_str = now.format("%H:%M:%S%.3f").to_string();
        let level = record.level();

        // 颜色 ANSI 码
        let (level_char, color, reset) = match level {
            Level::Error => ("e", "\x1B[31m", "\x1B[0m"), // 红
            Level::Warn => ("w", "\x1B[33m", "\x1B[0m"),  // 黄
            Level::Info => ("i", "\x1B[32m", "\x1B[0m"),  // 绿
            Level::Debug => ("d", "\x1B[36m", "\x1B[0m"), // 青
            Level::Trace => ("t", "\x1B[37m", "\x1B[0m"), // 白
        };

        // 控制台输出（彩色）
        let console_line = format!("{time_str} [{color}{level_char}{reset}] {}", record.args());
        let _ = writeln!(buf, "{}", console_line);

        // 文件输出（无颜色、按天切割）
        if let Ok(mut file) = daily_log_file(&log_dir) {
            let file_line = format!("{time_str} [{level_char}] {}", record.args());
            let _ = writeln!(file, "{}", file_line);
            let _ = file.flush();
        }
        Ok(())
    });

    // 忽略重复初始化错误
    let _ = builder.try_init();
}

/// 获取每日日志文件句柄
fn daily_log_file(log_dir: &PathBuf) -> std::io::Result<fs::File> {
    let today = Local::now().format("%Y-%m-%d").to_string();
    let log_file = log_dir.join(format!("{today}.log"));

    OpenOptions::new()
        .create(true)
        .append(true)
        .write(true)
        .open(log_file)
}

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
    init_logging();

    let app = tauri::Builder::default()
        .plugin(tauri_plugin_opener::init())
        .invoke_handler(tauri::generate_handler![greet])
        .setup(|_app: &mut App| {
            let resource_dir: PathBuf = get_resource_dir().map_err(|_| "无法获取资源目录")?;
            info!("资源目录: {:?}", resource_dir);

            let python_script: PathBuf = resource_dir.join("src-python/mxdict-server.py");
            info!("Python 脚本路径: {:?}", python_script);
            // let dist_dir: PathBuf = resource_dir.join("dist");

            // 启动 Python
            info!("准备启动 Python 服务器");
            let python_child = match std::process::Command::new("python3.11")
                .env(
        "PATH",
        "/opt/homebrew/bin:/usr/local/bin:/Library/Frameworks/Python.framework/Versions/3.11/bin:/usr/bin:/bin"
    )

                .arg(python_script)
                .spawn()
            {
                Ok(child) => {
                    info!("Python 服务器启动成功");
                    child
                },
                Err(e) => {
                    // 先打印错误日志
                    error!("启动 Python 服务器失败: {}", e);

                    // 再返回错误（让函数退出）
                    return Err(format!("启动 Python 服务器失败: {}", e).into());
                }
            };

            *PYTHON_PROCESS.lock().unwrap() = Some(python_child);

            if is_app_mode() {
                let dist_dir: PathBuf = resource_dir.join("dist");

                info!("准备启动 Node 服务器");
                let node_child = match std::process::Command::new("node")
        // 把常用 Python 路径优先加进去，兼容所有 macOS
               .env(
        "PATH",
        "/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin"
    )
                    .arg("/usr/local/bin/vite")
                    .arg("preview")
                    .arg("--port")
                    .arg("9595")
                    .arg("--strictPort")
                    .arg("--outDir")
                    .arg(dist_dir)
                    .spawn()
                {
                    Ok(child) => {
                        info!("Node 服务器启动成功");
                        child
                    },
                    Err(e) => {
                        // 先打印错误日志
                        error!("启动 Node 服务器失败: {}", e);
                        // 再返回错误（让函数退出）
                        return Err(format!("启动 Node 服务器失败: {}", e).into());
                    }
                };
                *NODE_PROCESS.lock().unwrap() = Some(node_child);
            }
            Ok(())
        })
        .build(tauri::generate_context!())
        .expect("error while building tauri application");

    app.run(|_, event: RunEvent| {
        if let RunEvent::Exit = event {
            if let Some(mut proc) = PYTHON_PROCESS.lock().unwrap().take() {
                info!("准备关闭 Python 服务器");
                let _ = proc.kill();
                let _ = proc.wait();
                info!("Python 服务器已关闭");
            }
            if let Some(mut proc) = NODE_PROCESS.lock().unwrap().take() {
                info!("准备关闭 Node 服务器");
                let _ = proc.kill();
                let _ = proc.wait();
                info!("Node 服务器已关闭");
            }
        }
    });
}
