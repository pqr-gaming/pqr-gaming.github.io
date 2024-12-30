import argparse
import pandas as pd
from datetime import datetime
import subprocess

# 读取CSV文件
def read_csv(file_path='data.csv'):
    try:
        return pd.read_csv(file_path)
    except FileNotFoundError:
        # 如果文件不存在，创建一个空的DataFrame
        return pd.DataFrame(columns=["名称", "中译名", "年份", "平台", "推荐指数", "添加时间"])

# 保存到CSV文件
def save_csv(df, file_path='data.csv'):
    df.to_csv(file_path, index=False)

# 更新条目
def update_entry(file_path, name, field, value):
    df = read_csv(file_path)
    if name in df["名称"].values:
        if field == "中译名" and value == '~':
            value = ""
        df.loc[df["名称"] == name, field] = value
        save_csv(df, file_path)
        print(f'条目 "{name}" 的 "{field}" 已更新为 "{value}"')
        return True
    else:
        print(f'未找到名称为 "{name}" 的条目。')
        return False

# 添加条目
def add_entry(file_path, name, chinese, year, platform, rating):
    df = read_csv(file_path)
    current_date = datetime.now().strftime("%Y/%m/%d")
    new_entry = pd.DataFrame({
        "名称": [name],
        "中译名": [chinese] if chinese != "~" else [""],
        "年份": [year],
        "平台": [platform],
        "推荐指数": [rating],
        "添加时间": [current_date]
    })
    df = pd.concat([df, new_entry], ignore_index=True)
    save_csv(df, file_path)
    print(f'已添加条目：\n{new_entry}')
    return True

# 删除条目
def delete_entry(file_path, name):
    df = read_csv(file_path)
    if name in df["名称"].values:
        df = df[df["名称"] != name]
        save_csv(df, file_path)
        print(f'已删除名称为 "{name}" 的条目。')
        return True
    else:
        print(f'未找到名称为 "{name}" 的条目。')
        return False

# 主函数，解析命令行参数
def main():
    parser = argparse.ArgumentParser(description="管理CSV文件中的条目")
    parser.add_argument("--file", type=str, default="PGDB.csv", help="CSV文件路径，默认为PGDB.csv")
    parser.add_argument("--update", type=str, help="要更新的条目名称")
    parser.add_argument("--field", type=str, choices=["名称", "中译名", "年份", "平台", "推荐指数", "添加时间"], help="要更新的字段名称")
    parser.add_argument("--value", type=str, help="更新的字段值")
    parser.add_argument("--add", nargs=5, metavar=("名称", "中译名[~ for empty]", "年份", "平台", "推荐指数"), help="添加条目", )
    parser.add_argument("--delete", type=str, help="要删除的条目名称")
    parser.add_argument("--sync", action="store_true", help="是否同步到Git仓库")

    args = parser.parse_args()

    updated = False
    if args.update and args.field and args.value:
        updated = update_entry(args.file, args.update, args.field, args.value)
    elif args.add:
        updated = add_entry(args.file, *args.add)
    elif args.delete:
        updated = delete_entry(args.file, args.delete)
    elif not args.sync:
        parser.print_help()

    if args.sync:
        try:
            subprocess.run(["git", "add", args.file], check=True)
            subprocess.run(["git", "commit", "-m", "add new entry"], check=True)
            subprocess.run(["git", "push", "origin", "main"], check=True)
            print("文件已成功提交并推送到 Git 仓库。")
        except subprocess.CalledProcessError as e:
            print("Git 操作失败:", e)


if __name__ == "__main__":
    main()
