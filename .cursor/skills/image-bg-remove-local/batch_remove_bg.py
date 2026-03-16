import argparse
from pathlib import Path

from PIL import Image
from rembg import remove

# 支持的图片格式
ALLOWED_FORMATS = (".jpg", ".jpeg", ".png", ".bmp", ".webp")


def ensure_dir(path: Path) -> None:
    """确保目录存在，不存在则自动创建。"""
    path.mkdir(parents=True, exist_ok=True)


def process_image(input_path: Path, output_path: Path) -> dict:
    """处理单张图片并返回结果。"""
    try:
        with Image.open(input_path) as img:
            output = remove(img)
            output.save(output_path, "PNG")
        return {"ok": True, "input": str(input_path), "output": str(output_path), "error": ""}
    except Exception as exc:
        return {"ok": False, "input": str(input_path), "output": str(output_path), "error": str(exc)}


def batch_process(input_folder: str = "input", output_folder: str = "output") -> dict:
    """
    批量去底，统一输出透明 PNG。
    返回结构化结果，便于命令行和 MCP 两边复用。
    """
    input_dir = Path(input_folder).resolve()
    output_dir = Path(output_folder).resolve()

    ensure_dir(input_dir)
    ensure_dir(output_dir)

    files = [p for p in input_dir.iterdir() if p.is_file() and p.suffix.lower() in ALLOWED_FORMATS]
    results = []
    success_count = 0
    fail_count = 0

    for file_path in files:
        output_path = output_dir / f"{file_path.stem}.png"
        result = process_image(file_path, output_path)
        results.append(result)
        if result["ok"]:
            success_count += 1
        else:
            fail_count += 1

    return {
        "input_dir": str(input_dir),
        "output_dir": str(output_dir),
        "total_candidates": len(files),
        "success_count": success_count,
        "fail_count": fail_count,
        "results": results,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="批量去除图片背景并输出透明 PNG。")
    parser.add_argument("--input", default="input", help="输入目录，默认 input")
    parser.add_argument("--output", default="output", help="输出目录，默认 output")
    args = parser.parse_args()

    report = batch_process(args.input, args.output)
    print("开始处理完成。")
    print(f"输入目录: {report['input_dir']}")
    print(f"输出目录: {report['output_dir']}")
    print(f"待处理数量: {report['total_candidates']}")
    print(f"成功数量: {report['success_count']}")
    print(f"失败数量: {report['fail_count']}")
    if report["fail_count"] > 0:
        print("失败明细:")
        for item in report["results"]:
            if not item["ok"]:
                print(f"- {item['input']} -> {item['error']}")


if __name__ == "__main__":
    main()
