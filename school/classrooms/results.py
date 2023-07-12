from dataclasses import dataclass

from school.courses.models import Course, LessonItem
from school.problems.models import Problem, Submit
from school.users.models import User


@dataclass
class ResultRow:
    user: User
    submits: list[Submit | None]


@dataclass
class Results:
    problems: list[Problem]
    rows: list[ResultRow]


def get_course_results(course: Course, users: list[User]) -> Results:
    items = (
        LessonItem.objects.filter(problem__isnull=False, lesson__course=course)
        .order_by(
            "lesson__course__coursegroup",
            "lesson__course",
            "lesson",
            "order",
        )
        .select_related("problem")
    )

    submits = (
        Submit.objects.filter(
            user__in=users,
            lesson_item__in=items,
        )
        .order_by("user_id", "lesson_item_id", "-created_at")
        .distinct("user_id", "lesson_item_id")
    )
    submit_map = {(s.user_id, s.lesson_item_id): s for s in submits}

    rows: list[ResultRow] = []
    for user in users:
        submits = []
        for item in items:
            submits.append(submit_map.get((user.id, item.id)))
        rows.append(ResultRow(user, submits))

    return Results([i.problem for i in items], rows)
