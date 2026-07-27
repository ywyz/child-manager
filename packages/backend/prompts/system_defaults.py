"""七个 v1 系统提示词的冻结只读资源。"""

SYSTEM_DEFAULTS: dict[str, str] = {
    "daily_activity_plan.morning_activity": (
        "请根据日期 {{plan_date}}、星期 {{weekday_text}}、教学周 {{teaching_week_text}}、"
        "季节 {{season}}、班级 {{class_name}}、年龄段 {{age_group_name}}与教师补充"
        " {{teacher_context}}，生成结构化晨间活动。"
    ),
    "daily_activity_plan.morning_talk": (
        "请根据日期 {{plan_date}}、星期 {{weekday_text}}、教学周 {{teaching_week_text}}、"
        "季节 {{season}}、班级 {{class_name}}、年龄段 {{age_group_name}}与教师补充"
        " {{teacher_context}}，生成结构化晨间谈话。"
    ),
    "daily_activity_plan.group_activity_split": (
        "请把原始集体活动 {{source_text}} 按 {{age_group_name}} 幼儿特点与教师补充"
        " {{teacher_context}} 拆分为结构化活动。"
    ),
    "daily_activity_plan.group_activity_add_step": (
        "请为集体活动 {{group_activity}} 按 {{age_group_name}} 幼儿特点与教师补充"
        " {{teacher_context}} 增加一个适龄环节。"
    ),
    "daily_activity_plan.indoor_area_game": (
        "请根据日期 {{plan_date}}、星期 {{weekday_text}}、教学周 {{teaching_week_text}}、"
        "季节 {{season}}、班级 {{class_name}}、年龄段 {{age_group_name}}、教师补充"
        " {{teacher_context}}与室内区域 {{indoor_areas}}，生成结构化区域游戏指导。"
    ),
    "daily_activity_plan.afternoon_outdoor_game": (
        "请根据日期 {{plan_date}}、星期 {{weekday_text}}、教学周 {{teaching_week_text}}、"
        "季节 {{season}}、班级 {{class_name}}、年龄段 {{age_group_name}}、教师补充"
        " {{teacher_context}}与户外区域 {{outdoor_areas}}，生成结构化户外游戏指导。"
    ),
    "daily_activity_plan.daily_reflection": (
        "请根据日期 {{plan_date}}、班级 {{class_name}}、年龄段 {{age_group_name}}和五个"
        "上游栏目 {{current_plan}}，生成结构化一日活动反思。"
    ),
}
