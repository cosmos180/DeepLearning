# 使用示例

## 场景 1: 查看所有收据
```
用户: 列出所有收据
AI:   运行 receipt_cli.py list-sheets
```

## 场景 2: 识别收据图片并保存
```
用户: 识别这张收据 ./receipt.jpg 并保存到 Excel
AI:   运行 receipt_cli.py recognize-and-save ./receipt.jpg
```

## 场景 3: 统计分析
```
用户: 显示月度汇总
AI:   运行 receipt_cli.py monthly --year 2025
```

## 场景 4: 搜索特定收据
```
用户: 搜索包含"打印"的收据
AI:   运行 receipt_cli.py search --keyword 打印
```

## 场景 5: 多步操作 - 识别后查看统计
```
用户: 识别 ./receipt.jpg 然后看看这个月花了多少
AI:   1. 运行 receipt_cli.py recognize-and-save ./receipt.jpg
      2. 运行 receipt_cli.py monthly
```

## 场景 6: 合并并美化
```
用户: 把这两个文件合并然后美化一下
AI:   1. 运行 receipt_cli.py merge --sources file1.xlsx,file2.xlsx
      2. 运行 receipt_cli.py beautify
```
