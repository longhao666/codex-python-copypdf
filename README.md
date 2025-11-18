# 功能说明

- 使用 python 脚本把文件夹下的所有 pdf 合并到一个 pdf 里面
- 示例
  - `python merge_pdfs.py --input-dir empty --output out.pdf --overwrite`
  - 多页拼板默认纵向并按列自上而下堆叠：`python merge_pdfs.py --input-dir empty --output out.pdf --pages-per-sheet 4`
  - 若需要横向拼板可加 `--orientation landscape`

其他常用参数请运行 `python merge_pdfs.py -h` 查看
