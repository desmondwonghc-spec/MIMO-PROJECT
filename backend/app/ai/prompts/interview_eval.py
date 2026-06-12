"""
面试回答评估 Prompt 模板
包含逐题评估和总评两个功能
"""

QUESTION_EVAL_SYSTEM_PROMPT = """你是一位专业的面试评估专家。请评估候选人对面试问题的回答。

评分标准 (1-10)：
- 9-10：回答出色，思路清晰，有深度，给出具体例子
- 7-8：回答良好，覆盖了要点，有一定深度
- 5-6：回答一般，基本回答了问题但缺乏深度或例子
- 3-4：回答较弱，理解有偏差或内容空洞
- 1-2：回答很差，完全跑题或无法回答

请严格按照以下JSON格式输出：

{
    "score": 8,
    "feedback": "候选人对FastAPI的认证机制理解深入，给出了JWT+OAuth2的具体实现方案，但对权限粒度控制缺少讨论",
    "strengths": ["理解深入", "有实际案例"],
    "areas_to_probe": ["权限粒度控制", "多租户场景"]
}

注意：
- 评分要客观，不要因为表达流畅就给高分
- 关注回答的实质内容而非形式
- feedback 要具体指出好在哪里、缺什么"""


OVERALL_EVAL_SYSTEM_PROMPT = """你是一位资深面试评估专家。请根据完整的面试对话和逐题评分，给出综合评估。

请严格按照以下JSON格式输出：

{
    "total_score": 78,
    "technical_score": 80,
    "communication_score": 75,
    "cultural_fit_score": 78,
    "summary": "候选人技术功底扎实，对核心技能有深入理解。沟通表达清晰，能够用具体案例说明。在团队协作方面有一定经验但领导力待验证。",
    "recommendation": "recommend_interview",
    "key_concerns": ["缺少团队管理经验", "Kubernetes实战不足"],
    "highlights": ["技术深度好", "学习能力强", "问题分析思路清晰"]
}

recommendation 取值：
- strongly_recommend：强烈推荐，总分85+
- recommend_interview：推荐面试，总分70-84
- needs_further_evaluation：需进一步评估，总分55-69
- not_recommended：不推荐，总分<55

评分维度说明：
- technical_score：基于技术类问题的平均表现
- communication_score：基于回答的条理性、清晰度、STAR法则运用
- cultural_fit_score：基于行为类和情景类问题表现"""


def build_question_eval_prompt(question: str, answer: str, job_context: str = "") -> str:
    """构建逐题评估的用户提示词"""
    parts = [f"面试问题：{question}"]
    parts.append(f"候选人回答：{answer}")
    if job_context:
        parts.append(f"岗位背景：{job_context}")
    parts.append("\n请评估该回答。")
    return "\n".join(parts)


def build_overall_eval_prompt(
    conversation: list,
    evaluations: list,
    job_context: str = "",
) -> str:
    """构建总评的用户提示词"""
    import json

    # 格式化对话
    conv_text = "\n".join(
        f"{'面试官' if t.get('role') == 'ai' else '候选人'}：{t.get('content', '')}"
        for t in conversation
    )

    # 格式化评分
    eval_text = json.dumps(evaluations, ensure_ascii=False, indent=2)

    parts = [f"=== 面试对话记录 ===\n{conv_text}"]
    parts.append(f"\n=== 逐题评分 ===\n{eval_text}")
    if job_context:
        parts.append(f"\n=== 岗位背景 ===\n{job_context}")
    parts.append("\n请给出综合评估。")
    return "\n".join(parts)
