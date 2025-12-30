from openai import OpenAI

client = OpenAI(base_url="http://127.0.0.1:1234/v1", api_key="lm-studio")

# 汤面（开场白）
open_context = "男人喝一口水,突然吐了出来"
# 汤底（真相）
main_context = "男人把盐当成糖,放到了水中"

def response(usr_input, system_prompt):
    try:
        completion = client.chat.completions.create(
            model="local-model",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": usr_input}
            ],
            temperature=0.0, # 逻辑判别任务建议 0.0，保持高度一致性
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"发生错误: {e}"

def get_ai_response(usr_input):
    # 1. 语义分析与合法性判断
    analyst_prompt = f"""
    【背景】：汤面为“{open_context}”。
    【任务】：分析用户问题。
    1. 提取主语和描述属性。
    2. 判断是否为是非题（可以用是/否回答）。
    3. 判断是否与故事主体相关。
    若不是是非题或完全无关，请在结论中写明“不合规”。
    """
    analyst_result = response(usr_input, analyst_prompt)
    
    # 如果分析阶段就判定不合规，直接拦截
    if "不合规" in analyst_result:
        return "我不知道 (请提问与故事相关的是非题)"

    # 2. 肯定证据列举 (Positive Chain)
    positive_prompt = f"""
    【真相】：{main_context}
    【分析报告】：{analyst_result}
    任务：请从【真相】中寻找证据，支持用户提问是真的。如果找不到，请说明原因。
    """
    pos_evidence = response(usr_input, positive_prompt)

    # 3. 否定证据列举 (Negative Chain)
    negative_prompt = f"""
    【真相】：{main_context}
    【分析报告】：{analyst_result}
    任务：请从【真相】中寻找证据，证明用户提问是假的。注意“未提及”也属于不支持。
    """
    neg_evidence = response(usr_input, negative_prompt)

    # 4. 最终裁决 (Final Judge)
    judge_prompt = f"""
    你是一个终审法官。请对比以下两份报告，给出“是的”、“不是”或“我不知道”。
    
    【肯定面证据】：{pos_evidence}
    【否定面证据】：{neg_evidence}
    
    【判定准则】：
    - 若肯定证据充分且无矛盾 -> 是的
    - 若否定证据明确（颜色、状态冲突） -> 不是
    - 若两边都没有确凿证据（真相未提及） -> 我不知道
    
    最终回答仅限词汇：是的、不是、我不知道。
    """
    
    final_decision = response(usr_input, judge_prompt)
    
    # 调试用：你可以打印出 pos 和 neg 看看它是如何“左右互搏”的
    print(f"DEBUG - Pos: {pos_evidence}\nNeg: {neg_evidence}")
    
    return final_decision