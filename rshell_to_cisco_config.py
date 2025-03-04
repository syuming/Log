import pandas as pd
import datetime
import os
from pathlib import Path


def rshell_to_cisco_config():

    # 取得腳本所在的資料夾路徑
    script_dir = Path(os.getcwd()).resolve()
    print(f"{script_dir}")


    file_path = os.path.join(script_dir, "RSHELL.csv")
    RSHELL_OK = os.path.join(script_dir, "RSHELL_OK.csv")
    RSHELL_to_abuseipdb = os.path.join(script_dir, "RSHELL_to_abuseipdb.csv")

    # 使用 Pandas
    df = pd.read_csv(file_path)

    # 假設要分割的欄位名稱為 'Message Text'
    df["Date_Time"], df["Message Text"] = zip(*df["Message Text"].str.split("%"))

    # 根據 'Message Text' 分組，並在每個組內保留 'Date' 最大的那一行
    df = df.sort_values("Date").groupby("Message Text").last().reset_index()

    # 拆分並取後半部分，同時保留原始欄位
    df["Source_IP"] = df["Message Text"].str.split(" ").str[-1]

    # 將日期欄位轉換為字符串類型並刪除連接符
    df["Date"] = df["Date"].astype(str).str.replace("-", "")

    # 將 Date 和 Time 欄位格式化並合併為 ISO 8601 格式的 Date_Time 欄位
    df["Date_Time2"] = pd.to_datetime(df["Date"] + " " + df["Time"]).dt.strftime(
        "%Y-%m-%dT%H:%M:%S+08:00"
    )

    # 假設您的 DataFrame 為 df，IP 位址欄為 'Source_IP'，日期欄為 'Date'
    def create_route_command(ip, Date):
        return f"ip route {ip} 255.255.255.255 Null0 name High_Risk_{Date}"

    df["route_command"] = df.apply(
        lambda x: create_route_command(x["Source_IP"], x["Date"]), axis=1
    )

    df.to_csv(RSHELL_OK, index=False, decimal=",")
    print(f"檔案已完成並匯出至%s" % RSHELL_OK)

    # 建立新的 df2
    df2 = pd.DataFrame(
        {
            "IP": df["Source_IP"],
            "Categories": ['18,22'] * len(df),  # 每列填入固定值，並加上雙引號
            "ReportDate": df["Date_Time2"],  # ReportDate 保持原樣，無雙引號
            "Comment": ['RCMD-4-RSHPORTATTEMPT: Attempted to connect to RSHELL,']
            * len(df),  # 每列固定填入文字，並加上雙引號
        }
    )

    # 自定義輸出方式，避免 ReportDate 被加上雙引號
    # df2.to_csv(RSHELL_to_abuseipdb, index=False, decimal=",", encoding="utf-8-sig", quoting=3, escapechar=' ')
    df2.to_csv(RSHELL_to_abuseipdb, index=False, decimal=",", encoding="utf-8-sig", )


if __name__ == "__main__":
    rshell_to_cisco_config()
    
