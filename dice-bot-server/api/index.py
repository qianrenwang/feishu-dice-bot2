"""
飞书骰子机器人 - Vercel Serverless 版本
部署到 Vercel 后，飞书 Webhook URL 设置为: https://你的域名/api/index
"""
import json
import random
import os
from http.server import BaseHTTPRequestHandler
from datetime import datetime

# 飞书机器人的 App ID 和 Secret（从飞书开放平台获取）
FEISHU_APP_ID = os.environ.get("FEISHU_APP_ID", "cli_aa881a6b85395bd7")
FEISHU_APP_SECRET = os.environ.get("FEISHU_APP_SECRET", "")

class DiceRoller:
    """骰子投掷器"""
    
    DICE_SHAPES = {
        6: ("🎲", "红色立方体"),
        10: ("⬡", "绿色五边形"),
        20: ("△", "蓝色三角形"),
        100: ("○", "紫色圆形")
    }
    
    @staticmethod
    def roll(min_val: int = 1, max_val: int = 6) -> dict:
        """投掷骰子并返回结果"""
        result = random.randint(min_val, max_val)
        
        # 根据最大值确定骰子类型
        if max_val == 6:
            emoji, shape = "🎲", "红色立方体"
        elif max_val == 10:
            emoji, shape = "⬡", "绿色五边形"
        elif max_val == 20:
            emoji, shape = "△", "蓝色三角形"
        elif max_val == 100:
            emoji, shape = "○", "紫色圆形"
        else:
            emoji, shape = "🎲", f"{min_val}-{max_val}自定义骰子"
        
        return {
            "result": result,
            "min": min_val,
            "max": max_val,
            "emoji": emoji,
            "shape": shape
        }
    
    @staticmethod
    def parse_command(text: str) -> dict:
        """解析用户指令，提取骰子类型"""
        text = text.lower().strip()
        
        # D6, D20, D100 格式
        if "d6" in text or "六面" in text or "6面" in text:
            return DiceRoller.roll(1, 6)
        elif "d10" in text or "十面" in text or "10面" in text:
            return DiceRoller.roll(1, 10)
        elif "d20" in text or "二十面" in text or "20面" in text:
            return DiceRoller.roll(1, 20)
        elif "d100" in text or "百面" in text or "100面" in text:
            return DiceRoller.roll(1, 100)
        
        # 范围格式：1-100, 1到100
        import re
        range_match = re.search(r'(\d+)\s*[-~到]\s*(\d+)', text)
        if range_match:
            min_val = int(range_match.group(1))
            max_val = int(range_match.group(2))
            return DiceRoller.roll(min_val, max_val)
        
        # 默认 1-6
        return DiceRoller.roll(1, 6)


def generate_dice_card(dice_result: dict) -> dict:
    """生成飞书卡片消息"""
    result = dice_result["result"]
    min_val = dice_result["min"]
    max_val = dice_result["max"]
    emoji = dice_result["emoji"]
    shape = dice_result["shape"]
    
    # 根据结果大小显示不同的提示语
    percentage = (result - min_val) / (max_val - min_val) if max_val > min_val else 0.5
    
    if percentage >= 0.9:
        luck = "🌟 运气爆棚！"
    elif percentage >= 0.7:
        luck = "✨ 运气不错~"
    elif percentage >= 0.4:
        luck = "🎯 中规中矩"
    elif percentage >= 0.2:
        luck = "😅 运气一般"
    else:
        luck = "💔 运气欠佳..."
    
    card = {
        "config": {
            "wide_screen_mode": True
        },
        "elements": [
            {
                "tag": "div",
                "text": {
                    "tag": "lark_md",
                    "content": f"**{emoji} {shape}**"
                }
            },
            {
                "tag": "div",
                "text": {
                    "tag": "lark_md",
                    "content": f"## 🎲 **{result}**"
                }
            },
            {
                "tag": "div",
                "text": {
                    "tag": "lark_md",
                    "content": f"范围：{min_val} - {max_val}  |  {luck}"
                }
            },
            {
                "tag": "hr"
            },
            {
                "tag": "div",
                "text": {
                    "tag": "lark_md",
                    "content": "💡 你可以这样投骰子：\n• @机器人 甩个六面骰\n• @机器人 D20\n• @机器人 1-100"
                }
            }
        ],
        "header": {
            "template": "blue",
            "title": {
                "content": "🎲 骰子结果",
                "tag": "plain_text"
            }
        }
    }
    
    return card


class handler(BaseHTTPRequestHandler):
    """Vercel Serverless Handler"""
    
    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)
        
        try:
            data = json.loads(post_data.decode('utf-8'))
            print(f"收到请求: {json.dumps(data, ensure_ascii=False)}")
            
            # 处理飞书事件
            response = self.handle_feishu_event(data)
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode('utf-8'))
            
        except Exception as e:
            print(f"错误: {str(e)}")
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))
    
    def do_GET(self):
        """健康检查"""
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({
            "status": "ok",
            "message": "骰子机器人服务运行中 🎲",
            "time": datetime.now().isoformat()
        }).encode('utf-8'))
    
    def handle_feishu_event(self, data: dict) -> dict:
        """处理飞书事件"""
        event_type = data.get("type", "")
        
        # URL 验证（首次配置 Webhook 时需要）
        if event_type == "url_verification":
            return {"challenge": data.get("challenge", "")}
        
        # 处理消息事件
        if event_type == "event_callback":
            event = data.get("event", {})
            msg_type = event.get("msg_type", "")
            
            # 只处理文本消息
            if msg_type == "text":
                message = event.get("message", {})
                content = json.loads(message.get("content", "{}"))
                text = content.get("text", "")
                
                # 检查是否艾特了机器人
                mentions = message.get("mentions", [])
                if mentions:
                    # 解析指令并投骰子
                    dice_result = DiceRoller.parse_command(text)
                    card = generate_dice_card(dice_result)
                    
                    # 返回卡片消息
                    return {
                        "code": 0,
                        "data": {
                            "content": json.dumps(card),
                            "msg_type": "interactive"
                        }
                    }
        
        return {"code": 0, "msg": "success"}


# 本地测试用
if __name__ == "__main__":
    # 测试骰子功能
    print("测试骰子功能：")
    
    test_cases = [
        "@机器人 甩个六面骰",
        "@机器人 D20",
        "@机器人 1-100",
        "@机器人 D10",
        "@机器人 D100"
    ]
    
    for cmd in test_cases:
        result = DiceRoller.parse_command(cmd)
        print(f"{cmd} -> {result['emoji']} {result['result']} ({result['shape']})")
