"""
简历解析器
验证和转换 AI 返回的简历结构化数据
"""
from typing import Optional
from app.models.resume import (
    ResumeStructuredData, Education, WorkExperience,
    LanguageProficiency, ExpectedSalary,
)


def parse_resume_data(ai_response: dict) -> ResumeStructuredData:
    """
    将 AI 返回的 JSON 解析为 ResumeStructuredData 模型
    处理缺失字段和数据标准化
    """
    # 处理教育经历
    education = []
    for edu in ai_response.get("education", []):
        if isinstance(edu, dict):
            education.append(Education(
                degree=_normalize_str(edu.get("degree", "")),
                institution=_normalize_str(edu.get("institution", "")),
                major=_normalize_str(edu.get("major", "")),
                start_year=edu.get("start_year"),
                end_year=edu.get("end_year"),
            ))

    # 处理工作经历
    work_experience = []
    for exp in ai_response.get("work_experience", []):
        if isinstance(exp, dict):
            work_experience.append(WorkExperience(
                company=_normalize_str(exp.get("company", "")),
                title=_normalize_str(exp.get("title", "")),
                start_date=_normalize_str(exp.get("start_date", "")),
                end_date=_normalize_str(exp.get("end_date", "")),
                duration_months=int(exp.get("duration_months", 0)),
                highlights=[_normalize_str(h) for h in exp.get("highlights", []) if h],
            ))

    # 处理语言能力
    languages = []
    for lang in ai_response.get("languages", []):
        if isinstance(lang, dict):
            level = _normalize_str(lang.get("level", "")).lower()
            if level not in ("native", "fluent", "intermediate", "basic"):
                level = "basic"
            languages.append(LanguageProficiency(
                language=_normalize_str(lang.get("language", "")),
                level=level,
            ))

    # 处理期望薪资
    expected_salary = None
    salary_data = ai_response.get("expected_salary")
    if salary_data and isinstance(salary_data, dict) and salary_data.get("amount"):
        expected_salary = ExpectedSalary(
            amount=float(salary_data["amount"]),
            currency=salary_data.get("currency", "CNY"),
        )

    # 处理年龄
    age = ai_response.get("age")
    if age is not None:
        try:
            age = int(age)
            if age < 16 or age > 70:
                age = None
        except (ValueError, TypeError):
            age = None

    return ResumeStructuredData(
        name=_normalize_str(ai_response.get("name", "")),
        email=_normalize_str(ai_response.get("email", "")),
        phone=_normalize_str(ai_response.get("phone", "")),
        age=age,
        gender=_normalize_str(ai_response.get("gender", "")),
        current_location=_normalize_str(ai_response.get("current_location", "")),
        summary=_normalize_str(ai_response.get("summary", ""))[:200],
        education=education,
        work_experience=work_experience,
        total_experience_years=float(ai_response.get("total_experience_years", 0)),
        skills=[_normalize_str(s) for s in ai_response.get("skills", []) if s],
        certifications=[_normalize_str(c) for c in ai_response.get("certifications", []) if c],
        languages=languages,
        expected_salary=expected_salary,
    )


def _normalize_str(value) -> str:
    """标准化字符串：去首尾空白"""
    if value is None:
        return ""
    return str(value).strip()
