"""
飞书骰子机器人 - 本地测试 + ngrok 版本
适合快速测试，不需要购买服务器
"""
from flask import Flask, request, jsonify
import json
import random

app = Flask(__name__)


class DiceRoller:
    """骰子投掷器"""
    
    @staticmethod
    def roll(min_val: int = 1, max_val: int = 6) -> dict:
        result = random.randint(min_val, max_val)
        
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
        
        return {"result": result, "min": min_val, "max": max_val, "emoji": emoji, "shape": shape}
    
    @staticmethod
    def parse_command(text: str) -> dict:
        text = text.lower().strip()
        
        if "d6" in text or "六面" in text or "6面" in text:
            return DiceRoller.roll(1, 6)
        elif "d10" in text or "十面" in text or "10面" in text:
            return DiceRoller.roll(1, 10)
        elif "d20" in text or "二十面" in text or "20面" in text:
            return DiceRoller.roll(1, 20)
        elif "d100" in text or "百面" in text or "100面" in text:
            return DiceRoller.roll(1, 100)
        
        import re
        range_match = re.search(r'(\d+)\s*[-~到]\s*(\d+)', text)
        if range_match:
            return DiceRoller.roll(int(range_match.group(1)), int(range_match.group(2)))
        
        return DiceRoller.roll(1, 6)


def generate_card(dice_result: dict) -> dict:
    result = dice_result["result"]
    min_val, max_val = dice_result["min"], dice_result["max"]
    emoji, shape = dice_result["emoji"], dice_result["shape"]
    
    percentage = (result - min_val) / (max_val - min_val) if max_val > min_val else 0.5
    luck = "🌟 运气爆棚！" if percentage >= 0.9 else \
           "✨ 运气不错~" if percentage >= 0.7 else \
           "🎯 中规中矩" if percentage >= 0.4 else \
           "😅 运气一般" if percentage >= 0.2 else "💔 运气欠佳..."
    
    return {
        "config": {"wide_screen_mode": True},
        "elements": [
            {"tag": "div", "text": {"tag": "lark_md", "content": f"**{emoji} {shape}**"}},
            {"tag": "div", "text": {"tag": "lark_md", "content": f"## 🎲 **{result}**"}},
            {"tag": "div", "text": {"tag": "lark_md", "content": f"范围：{min_val} - {max_val}  |  {luck}"}},
            {"tag": "hr"},
            {"tag": "div", "text": {"tag": "lark_md", "content": "💡 你可以这样投骰子：\n• @机器人 甩个六面骰\n• @机器人 D20\n• @机器人 1-100"}}
        ],
        "header": {"template": "blue", "title": {"content": "🎲 骰子结果", "tag": "plain_text"}}
    }


@app.route('/webhook', methods=['POST'])
def webhook():
    """飞书 Webhook 入口"""
    data = request.get_json()
    print(f"收到请求: {json.dumps(data, ensure_ascii=False)}")
    
    # URL 验证
    if data.get("type") == "url_verification":
        return jsonify({"challenge": data.get("challenge", "")})
    
    # 处理消息
    if data.get("type") == "event_callback":
        event = data.get("event", {})
        
        if event.get("msg_type") == "text":
            message = event.get("message", {})
            content = json.loads(message.get("content", "{}"))
            mentions = message.get("mentions", [])
            
            if mentions:
                text = content.get("text", "")
                dice_result = DiceRoller.parse_command(text)
                card = generate_card(dice_result)
                
                return jsonify({
                    "code": 0,
                    "data": {
                        "content": json.dumps(card),
                        "msg_type": "interactive"
                    }
                })
    
    return jsonify({"code": 0, "msg": "success"})


@app.route('/health', methods=['GET'])
def health():
    """健康检查"""
    return jsonify({"status": "ok", "message": "骰子机器人运行中 🎲"})


@app.route('/test', methods=['GET'])
def test():
    """测试页面 - 显示一个示例骰子结果"""
    dice_result = DiceRoller.roll(1, 20)
    return jsonify(dice_result)


if __name__ == '__main__':
    print("🎲 骰子机器人启动中...")
    print("访问 http://localhost:5000/health 测试服务")
    print("访问 http://localhost:5000/test 查看示例结果")
    app.run(host='0.0.0.0', port=5000, debug=True)