from openai import OpenAI

client = OpenAI(base_url="http://127.0.0.1:1234/v1", api_key="lm-studio")

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

# 返回到前端
def get_ai_response(usr_input, open_context, main_context):
    # 1. 语义分析与合法性判断
    analyst_prompt = f"""
    【知识要点】：语义成分的分解：论元结构（Argument Structure）
    在语义层面，语言学把判断句看作一场“戏”，动词是剧本（谓词），名词是演员（论元）。
    分解方式： 提取核心谓词，并确定其题元角色（Thematic Roles）。
    分析逻辑： * 施事（Agent）： 动作的发出者,或者起到影响作用的主体。
    受事（Patient）： 动作的承受者，或者被作用的主体。
    其中【施事】可能通过第三个【间接/参与主体】传递到【受事】
    工具/地点/时间： 辅助性成分。
    需要的判断： * 选择限制判断： 比如“吃”这个谓词，要求其“施事”通常必须是有生命的。
    配价判断： 这个动词需要几个论元？（“死”是一价，“爱”是二价，“给”是三价）。

    【警惕】警惕用户引入【现实】，必须只能在这个【背景】下讨论，引入【现实】必须警惕的思考是否和【背景】相关，尤其警惕“我”“你”“他们”“今天”的字眼
    【背景】：汤面为“{open_context}”汤底为“{main_context}”。
    【任务】：
    a.分析【背景】中所有的【工具/地点/时间】、【修饰词】-【名词】、【施事人/物】、【受事人/物】、【谓语】、【间接/参与主体】
    b.分析用户的输入。
    1. 分析句子的组成成分, 【工具/地点/时间】、【修饰词】-【名词】、【施事人/物】、【受事人/物】、【谓语】、【间接/参与主体】, 其中【修饰词】和【名词】要一一对应
    2. 判断是否为是非题（可以用是/否回答），一定要有【施事人/物】、【受事人/物】、【谓语】。“你好”这样的句子不是一个判断句。
    3. 判断是否与【背景】相关，对比【背景】中是否有【施事人/物】、【受事人/物】、【间接/参与主体】，如果有其中之一那么大概率相关，如果都没有没有大概率无关。
    若不是是非题或完全无关，请在结论中写明“不合规”。
    """
    analyst_result = response(usr_input, analyst_prompt)
    
    print(f"DEBUG - Analys: {analyst_result}\n")
    # 如果分析阶段就判定不合规，直接拦截
    if "不合规" in analyst_result:
        return "我不知道 (请提问与故事相关的是非题)"

    # 2. 肯定证据列举 (Positive Chain)
    positive_prompt = f"""
    只能从【真相】中直接对比，不能推断【真相】，不要思考“表明”“可能”“应该”的方式
    【真相】：{main_context}
    【分析报告】：{analyst_result}
    任务：请从【真相】中寻找证据，支持用户提问是真的。如果找不到，请说明原因。
    """
    pos_evidence = response(usr_input, positive_prompt)

    # 3. 否定证据列举 (Negative Chain)
    negative_prompt = f"""
    只能从【真相】中直接对比，不能推断【真相】，不要思考“表明”“可能”“应该”的方式
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
    - 只能从【真相】中直接对比，不能推断【真相】
    - 若肯定证据充分且无矛盾 -> 是的
    - 若否定证据明确（颜色、状态冲突） -> 不是
    - 若两边都没有确凿证据（真相未提及） -> 我不知道
    
    最终回答仅限词汇：是的、不是、我不知道。
    """
    
    final_decision = response(usr_input, judge_prompt)
    
    # 调试用：你可以打印出 pos 和 neg 看看它是如何“左右互搏”的
    print(f"DEBUG - Pos: {pos_evidence}\nNeg: {neg_evidence}\n")
    
    return final_decision