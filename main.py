import os
import sys
import json
import socket

# 飞书卡片源代码
CARD_SRC = r'''
{
    "config": {
        "update_multi": true
    },
    "i18n_elements": {
        "zh_cn": [
            {
                "tag": "column_set",
                "flex_mode": "none",
                "background_style": "default",
                "horizontal_spacing": "8px",
                "horizontal_align": "left",
                "columns": [
                    {
                        "tag": "column",
                        "width": "weighted",
                        "vertical_align": "top",
                        "vertical_spacing": "8px",
                        "background_style": "default",
                        "elements": [
                            {
                                "tag": "markdown",
                                "content": "**开始时间：**\n${time_start}",
                                "text_align": "left",
                                "text_size": "normal"
                            }
                        ],
                        "weight": 1
                    },
                    {
                        "tag": "column",
                        "width": "weighted",
                        "vertical_align": "top",
                        "vertical_spacing": "8px",
                        "background_style": "default",
                        "elements": [
                            {
                                "tag": "markdown",
                                "content": "**结束时间：**\n${time_end}",
                                "text_align": "left",
                                "text_size": "normal"
                            }
                        ],
                        "weight": 1
                    }
                ],
                "margin": "16px 0px 0px 0px"
            },
            {
                "tag": "column_set",
                "flex_mode": "none",
                "background_style": "default",
                "horizontal_spacing": "8px",
                "horizontal_align": "left",
                "columns": [
                    {
                        "tag": "column",
                        "width": "weighted",
                        "vertical_align": "top",
                        "vertical_spacing": "8px",
                        "background_style": "default",
                        "elements": [
                            {
                                "tag": "markdown",
                                "content": "**Host:**\n${host}\n**Exit code**:\n${code}",
                                "text_align": "left",
                                "text_size": "normal"
                            }
                        ],
                        "weight": 1
                    },
                    {
                        "tag": "column",
                        "width": "weighted",
                        "vertical_align": "top",
                        "vertical_spacing": "0px",
                        "background_style": "default",
                        "elements": [
                            {
                                "tag": "markdown",
                                "content": "**Time cost:**",
                                "text_align": "left",
                                "text_size": "normal"
                            },
                            {
                                "tag": "column_set",
                                "flex_mode": "none",
                                "background_style": "default",
                                "horizontal_spacing": "8px",
                                "horizontal_align": "left",
                                "columns": [
                                    {
                                        "tag": "column",
                                        "width": "30px",
                                        "vertical_align": "top",
                                        "vertical_spacing": "8px",
                                        "background_style": "default",
                                        "elements": [
                                            {
                                                "tag": "markdown",
                                                "content": "real\nuser\nsys",
                                                "text_align": "left",
                                                "text_size": "normal"
                                            }
                                        ]
                                    },
                                    {
                                        "tag": "column",
                                        "width": "auto",
                                        "vertical_align": "top",
                                        "vertical_spacing": "8px",
                                        "background_style": "default",
                                        "elements": [
                                            {
                                                "tag": "markdown",
                                                "content": "${time}",
                                                "text_align": "left",
                                                "text_size": "normal"
                                            }
                                        ]
                                    }
                                ],
                                "margin": "0px 0px 0px 0px"
                            }
                        ],
                        "weight": 1
                    }
                ],
                "margin": "16px 0px 0px 0px"
            },
            {
                "tag": "markdown",
                "content": "<font color='gray'>Log 保存在 ${root}</font>",
                "text_align": "left",
                "text_size": "normal"
            },
            {
                "tag": "hr"
            },
            {
                "tag": "markdown",
                "content": "**Output:**\n```\n${log}\n```",
                "text_align": "left",
                "text_size": "normal"
            }
        ]
    },
    "i18n_header": {
        "zh_cn": {
            "title": {
                "tag": "plain_text",
                "content": "Success"
            },
            "subtitle": {
                "tag": "plain_text",
                "content": "${cmd}"
            },
            "template": "green",
            "ud_icon": {
                "tag": "standard_icon",
                "token": "done_outlined"
            }
        }
    }
}
'''


def format_feishu_card(card: str, data: dict) -> dict:
    '''把飞书卡片源代码转成字典, 并替换所有变量'''

    def traverse_values(d):
        '''递归遍历字典中, 所有值是str的键值对'''
        for k, v in d.items():
            if isinstance(v, str):
                yield d, k, v
            elif isinstance(v, dict):
                yield from traverse_values(v)
            elif isinstance(v, list):
                for i in v:
                    yield from traverse_values(i)

    card: dict = json.loads(card)
    for d, k, v in traverse_values(card):
        d[k] = v.replace("${", "{").format(**data)
    return card


def get_run_data(root) -> dict:
    '''从任务目录中获取程序运行的各种数据'''
    data = {}

    data['root'] = os.path.abspath(root)

    with open(os.path.join(root, 'log')) as f:
        log = f.readlines()[1:-2]
        log = ''.join(log[-10:]).strip()
        data['log'] = log

    with open(os.path.join(root, 'time-start')) as f:
        data['time_start'] = f.read().strip()

    with open(os.path.join(root, 'time-end')) as f:
        data['time_end'] = f.read().strip()

    data['host'] = socket.gethostname()

    with open(os.path.join(root, 'status')) as f:
        code = int(f.read().strip())
        data['code'] = code

    with open(os.path.join(root, 'time')) as f:
        result = []
        for l in f:
            l = l.strip()
            if not l:
                continue
            result.append(l.strip().split()[1])
        data['time'] = '\n'.join(result)

    with open(os.path.join(root, 'go.sh')) as f:
        data['cmd'] = f.readlines()[-1].strip()

    return data


if __name__ == "__main__":
    root = sys.argv[1]

    data = get_run_data(root)
    card = format_feishu_card(CARD_SRC, data)

    # 如果程序运行失败，修改卡片的标题和颜色
    if data['code'] != 0:
        header = card['i18n_header']['zh_cn']
        header['title']['content'] = 'Failed'
        header['template'] = 'red'
        header['ud_icon']['token'] = 'close_outlined'

    print(json.dumps({
        "msg_type": "interactive",
        "card": card
    }))
