#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from docx import Document
import json

def read_skill_sheet(filepath):
    """スキルシートの構造を読み取って分析"""
    doc = Document(filepath)
    
    content = {
        "tables": [],
        "paragraphs": []
    }
    
    # テーブルの内容を抽出
    for i, table in enumerate(doc.tables):
        table_data = []
        for row in table.rows:
            row_data = []
            for cell in row.cells:
                row_data.append(cell.text.strip())
            table_data.append(row_data)
        content["tables"].append({
            "index": i,
            "data": table_data
        })
    
    # パラグラフの内容を抽出
    for para in doc.paragraphs:
        if para.text.strip():
            content["paragraphs"].append(para.text.strip())
    
    return content

if __name__ == "__main__":
    filepath = "/Users/tomo/EG/スキルシート/【F・T】スキルシート.docx"
    content = read_skill_sheet(filepath)
    
    print("=== スキルシートの構造 ===\n")
    
    print(f"テーブル数: {len(content['tables'])}")
    print(f"パラグラフ数: {len(content['paragraphs'])}\n")
    
    # 各テーブルの概要を表示
    for i, table in enumerate(content['tables']):
        print(f"\n--- テーブル {i+1} ---")
        # 最初の数行を表示
        for j, row in enumerate(table['data'][:5]):
            if j == 0:  # ヘッダー行の可能性
                print(f"ヘッダー候補: {row}")
            else:
                print(f"行{j}: {row[:3]}...")  # 最初の3列のみ表示
        if len(table['data']) > 5:
            print(f"... (残り {len(table['data']) - 5} 行)")
    
    # パラグラフの概要
    print("\n--- パラグラフ ---")
    for para in content['paragraphs'][:10]:
        print(f"- {para[:50]}..." if len(para) > 50 else f"- {para}")