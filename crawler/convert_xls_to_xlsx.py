#-----------------XLS->XLSX--------------------
def convert_xls_to_xlsx_clean(xls_path):
    xlsx_path = xls_path.with_suffix(".xlsx")

    # 读取 xls（仅读值，不读样式）
    book = xlrd.open_workbook(xls_path, formatting_info=False)
    sheet = book.sheet_by_index(0)

    # 创建全新的 XLSX —— 无样式污染
    wb = Workbook()
    ws = wb.active

    # 设置默认列宽，使移动端可见
    for col in range(1, sheet.ncols + 1):
        column_letter = chr(64 + col)
        ws.column_dimensions[column_letter].width = 25

    # 写入内容并设置统一样式
    for r in range(sheet.nrows):
        row_values = sheet.row_values(r)
        ws.append(row_values)

        for c in range(1, len(row_values) + 1):
            cell = ws.cell(row=r+1, column=c)
            cell.font = Font(color="000000")             # 强制黑色字体
            cell.alignment = Alignment(
                wrap_text=True,                          # 自动换行
                vertical="top",
                horizontal="left"
            )

    wb.save(xlsx_path)
    return xlsx_path

#----------------清洗单元格内容：去除前置换行符------------------
def clean_xlsx_content(path):
    wb = openpyxl.load_workbook(xlsx_path)
    ws = wb.active

    # 自动换行、固定行高
    for row in ws.iter_rows():
        for cell in row:
            if cell.value:
                cell.alignment = Alignment(
                    wrap_text=True,  # 自动换行
                    vertical="top"  # 顶部对齐
                )

    # 设置每行行高（移动端才会显示多行）
    for row in ws.iter_rows():
        row_index = row[0].row
        ws.row_dimensions[row_index].height = 110

    # 可选：列宽固定，让课程不被压扁
    for col in range(2, 9):  # 星期一到星期日
        ws.column_dimensions[get_column_letter(col)].width = 22

    wb.save(xlsx_path)
    return xlsx_path

