"""
飞书骰子机器人 - 阿里云函数计算版本
"""
import json
import random
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)


class DiceRoller:
    """骰子投掷器"""
    
    @staticmethod
    def roll(min_val: int = 1, max_val: int = 6) -> dict:
        """投掷骰子并返回结果"""
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
        
        return {
            "result": result,
            "min": min_val,
            "max": max_val,
            "emoji": emoji,
            "shape": shape
        }
    
    @staticmethod
    def parse_command(text: str) -> dict:
        """解析用户指令"""
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
            min_val = int(range_match.group(1))
            max_val = int(range_match.group(2))
            return DiceRoller.roll(min_val, max_val)
        
        return DiceRoller.roll(1, 6)


def generate_response(dice_result: dict) -> dict:
    """生成回复消息"""
    result = dice_result["result"]
    min_val = dice_result["min"]
    max_val = dice_result["max"]
    emoji = dice_result["emoji"]
    shape = dice_result["shape"]
    
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
    
    return {
        "code": 0,
        "data": {
            "content": json.dumps({
                "config": {"wide_screen_mode": True},
                "elements": [
                    {"tag": "div", "text": {"tag": "lark_md", "content": f"**{emoji} {shape}**"}},
                    {"tag": "div", "text": {"tag": "lark_md", "content": f"## 🎲 **{result}**"}},
                    {"tag": "div", "text": {"tag": "lark_md", "content": f"范围：{min_val} - {max_val}  |  {luck}"}},
                    {"tag": "hr"},
                    {"tag": "div", "text": {"tag": "lark_md", "content": "💡 你可以这样投骰子：\n• @机器人 甩个六面骰\n• @机器人 D20\n• @机器人 1-100"}}
                ],
                "header": {
                    "template": "blue",
                    "title": {"content": "🎲 骰子结果", "tag": "plain_text"}
                }
            }),
            "msg_type": "interactive"
        }
    }


def handler(event, context):
    """阿里云函数计算入口"""
    logger.info(f"收到事件: {event}")
    
    try:
        # 解析请求
        if isinstance(event, str):
            data = json.loads(event)
        elif isinstance(event, bytes):
            data = json.loads(event.decode('utf-8'))
        else:
            data = event
        
        # URL 验证
        if data.get("type") == "url_verification":
            return {
                "statusCode": 200,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"challenge": data.get("challenge", "")})
            }
        
        # 处理消息事件
        if data.get("type") == "event_callback":
            event_data = data.get("event", {})
            
            if event_data.get("msg_type") == "text":
                message = event_data.get("message", {})
                content = json.loads(message.get("content", "{}"))
                text = content.get("text", "")
                mentions = message.get("mentions", [])
                
                if mentions:
                    dice_result = DiceRoller.parse_command(text)
                    response = generate_response(dice_result)
                    
                    return {
                        "statusCode": 200,
                        "headers": {"Content-Type": "application/json"},
                        "body": json.dumps(response)
                    }
        
        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"code": 0, "msg": "success"})
        }
        
    except Exception as e:
        logger.error(f"处理错误: {str(e)}")
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": str(e)})
        }