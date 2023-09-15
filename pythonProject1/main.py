import requests
import os
import re
from bs4 import BeautifulSoup

import tkinter as tk
from tkinter import ttk


def scrape_problems(difficulty, keywords):
    url = "https://www.luogu.com.cn/problem/list?difficulty={}&tag={}".format(difficulty, keywords)
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    problems = soup.find_all("div", class_="lg-content-item lg-problem-cell")

    directory_name = "{}-{}".format(difficulty, "-".join(keywords.split()))
    os.makedirs(directory_name, exist_ok=True)

    for problem in problems:
        # 解析题目编号、标题和链接
        problem_id = problem.find("span", class_="problem-id").text.strip()
        title_tag = problem.find("a", class_="lg-right")
        problem_title = title_tag.text.strip()
        problem_link = "https://www.luogu.com.cn" + title_tag["href"]

        # 解析题解链接
        solution_link = ""
        solution_tags = problem.find_all("a", class_="lg-right")
        for tag in solution_tags:
            if "题解" in tag.text:
                solution_link = "https://www.luogu.com.cn" + tag["href"]
                break

        # 创建题目文件夹
        folder_name = "{}-{}".format(problem_id, problem_title)
        os.makedirs(folder_name, exist_ok=True)

        # 爬取题目内容并保存为markdown文件
        problem_response = requests.get(problem_link)
        problem_soup = BeautifulSoup(problem_response.text, "html.parser")
        problem_content = problem_soup.find("div", class_="lg-article am-g").prettify()
        with open(os.path.join(folder_name, "{}-{}.md".format(problem_id, problem_title)), "w", encoding="utf-8") as f:
            f.write(problem_content)

        # 爬取题解内容并保存为markdown文件
        if solution_link:
            solution_response = requests.get(solution_link)
            solution_soup = BeautifulSoup(solution_response.text, "html.parser")
            solution_content = solution_soup.find("div", class_="lg-article am-g").prettify()
            with open(os.path.join(folder_name, "{}-{}-题解.md".format(problem_id, problem_title)), "w",
                      encoding="utf-8") as f:
                f.write(solution_content)

        # 移动题目文件夹到相应的目录下
        os.rename(folder_name, os.path.join(directory_name, folder_name))


# 处理搜索按钮点击事件
def search_button_clicked():
    difficulty = difficulty_combobox.get()
    keywords = keywords_entry.get()
    scrape_problems(difficulty, keywords)


# 创建GUI界面
window = tk.Tk()
window.title("题目爬虫")
window.geometry("400x200")

# 题目难度选择下拉框
difficulty_label = tk.Label(window, text="难度：")
difficulty_label.pack()
difficulty_combobox = ttk.Combobox(window, width=20)
difficulty_combobox['values'] = ["暂无评定入门", "普及-", "普及/提高-", "普及+/提高", "提高+/省选-", "省选/NOI-",
                                 "NOI/NOI+/CTSC"]
difficulty_combobox.pack()

# 关键词输入框
keywords_label = tk.Label(window, text="关键词：")
keywords_label.pack()
keywords_entry = tk.Entry(window, width=30)
keywords_entry.pack()

# 搜索按钮
search_button = tk.Button(window, text="搜索", command=search_button_clicked)
search_button.pack()

window.mainloop()