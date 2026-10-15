import os
import shutil
import sys
import time
import zipfile
from pathlib import Path

sys.dont_write_bytecode = True


def _win_add_data(src: str, dest: str) -> str:
    """Format --add-data argument for PyInstaller on Windows."""
    # PyInstaller on Windows expects 'src;dest'
    return f"{src};{dest}"
def build():
    work_dir = Path.cwd()

    exe_name = "乌有乡游记"
    dist_base = work_dir / "dist"
    release_dir = work_dir / "releases"
    release_dir.mkdir(exist_ok=True)

    # Prepare PyInstaller params
    params = [
        str(work_dir / "main.py"),
        f"--name={exe_name}",
        "--onedir",
        "--noconfirm",
        "--windowed",
        "--clean",
    ]

    # Hidden imports that often cause runtime issues
    hidden_imports = ["PIL", "src", "tiktoken", "tiktoken_ext", "tiktoken_ext.openai_public", "tiktoken_ext.plugin"]
    for hi in hidden_imports:
        params.append(f"--hidden-import={hi}")

    # Add data folders (Assets, Save/config) so the exe can find resources
    assets_src = work_dir / "Assets"
    if assets_src.exists():
        params.append(f"--add-data={_win_add_data(str(assets_src), 'Assets')}")

    # If icon exists, use it for the exe
    icon_path = work_dir / "Assets" / "Images" / "GameIcon" / "icon.ico"
    if icon_path.exists():
        params.append(f"--icon={str(icon_path)}")
    else:
        print("提示: 未找到游戏图标，继续不使用图标构建。")

    save_dir = work_dir / "Save"
    if (save_dir / "config.lzn").exists():
        params.append(f"--add-data={_win_add_data(str(save_dir / 'config.lzn'), 'Save/config.lzn')}")

    print("开始使用 PyInstaller 打包...")
    try:
        import PyInstaller.__main__

        PyInstaller.__main__.run(params)
    except Exception as e:
        print("错误: 运行 PyInstaller 失败。请确认已安装 PyInstaller。")
        raise

    # Determine actual dist dir
    dist_dir = dist_base / exe_name
    if not dist_dir.exists():
        # PyInstaller may use just dist/<name> or dist/<exe_name>
        # Fallback: find first directory under dist
        children = [p for p in dist_base.iterdir() if p.is_dir()]
        dist_dir = children[0] if children else dist_dir

    print("打包完成。正在整理生成物并生成 requirements.txt ...")

    # Ensure Save/saves exists in dist
    dist_save = dist_dir / "Save"
    (dist_save / "saves").mkdir(parents=True, exist_ok=True)

    # Copy config.lzn if exists
    src_config = save_dir / "config.lzn"
    if src_config.exists():
        shutil.copy2(src_config, dist_save / "config.lzn")
        print(f"已复制配置文件: {src_config} -> {dist_save / 'config.lzn'}")

    # Ensure Assets copied (PyInstaller --add-data already bundles, but copy for safety)
    if assets_src.exists():
        dst_assets = dist_dir / "Assets"
        if dst_assets.exists():
            shutil.rmtree(dst_assets)
        shutil.copytree(assets_src, dst_assets)
        print(f"已复制 Assets 到：{dst_assets}")
    else:
        print("警告: 未找到 Assets 目录")

    # Generate requirements.txt using current python interpreter
    req_file = dist_dir / "requirements.txt"
    try:
        import subprocess

        print("正在生成 requirements.txt...")
        out = subprocess.check_output([sys.executable, "-m", "pip", "freeze"], text=True)
        req_file.write_text(out, encoding="utf-8")
        print(f"requirements.txt 已写入: {req_file}")
    except Exception as e:
        print(f"生成 requirements.txt 失败: {e}")

    # Create a zip of the dist folder for release
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    zip_name = release_dir / f"{exe_name}_{timestamp}.zip"
    print(f"正在创建发行包: {zip_name}")
    with zipfile.ZipFile(zip_name, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(dist_dir):
            for f in files:
                full = Path(root) / f
                rel = full.relative_to(dist_dir.parent)
                zf.write(full, rel)

    print("\n构建与打包完成！")
    print(f"生成目录: {dist_dir}")
    print(f"发行压缩包: {zip_name}")


if __name__ == "__main__":
    build()
