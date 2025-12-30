from openai import OpenAI

# 1. 初始化客户端
# base_url 必须指向 LM Studio 的地址
# api_key 在本地部署中通常随便填一个字符串即可，LM Studio 不校验它
client = OpenAI(base_url="http://127.0.0.1:1234/v1", api_key="lm-studio")

abc = '''
# 设定
你是一个死板的逻辑核查员。

# 核心事实（唯一标准）
- 【小红】：穿着[黄色袜子]、[红色鞋子]
- 【鸭子】：颜色是[蓝色]、正在[游过河]
- 【小河】：颜色是[红色]

# 严格判定逻辑
1. **完全匹配**：只有当 [主体] 与 [属性] 完全符合上述事实时，回“是的”。
2. **明确冲突**：如果 [主体] 已在事实中，但 [属性] 被替换（如：蓝色鸭子说成红色鸭子），必须回“不是”。
3. **主体不存在**：如果问题涉及上述核心事实之外的主体（如：天气、太阳、人类、死亡），必须回“我不知道”。
4. **属性不存在**：如果主体存在，但询问的属性未提及（如：小红的年龄、鸭子的品种），必须回“我不知道”。

# 回复规范
- 仅输出：是的 / 不是 / 我不知道
- 禁止任何推理、联想或解释。

# 测试：
问：“蓝色鸭子是红色的吗？” -> 答：不是（因为事实中鸭子是蓝色的）
问：“小红是人类吗？” -> 答：我不知道（因为事实没写物种）

# 请处理以下输入：
“{{用户提问}}”
'''

def get_ai_response(user_input):
    try:
        # 2. 发起请求
        completion = client.chat.completions.create(
            model="local-model", # 这个参数在 LM Studio 中通常会被忽略，默认使用你加载的模型
            messages=[
                {"role": "system", "content": abc},
                {"role": "user", "content": user_input}
            ],
            temperature=0.1,
        )

        # 3. 提取输出
        return completion.choices[0].message.content

    except Exception as e:
        return f"发生错误: {e}"
    
def stream_response(user_input):
    response = client.chat.completions.create(
        model="local-model",
        messages=[{"role": "user", "content": user_input}],
        stream=True,
    )
    
    for chunk in response:
        if chunk.choices[0].delta.content:
            print(chunk.choices[0].delta.content, end="", flush=True)

# 4. 测试输入输出
if __name__ == "__main__":
    # user_query = "请解释一下什么是量子纠缠？"
    # print(f"用户输入: {user_query}")
    
    # result = get_ai_response(user_query)
    
    # print("-" * 20)
    # print(f"模型输出:\n{result}")
    # 调用
    stream_response("写一篇关于未来城市的科幻短文。")