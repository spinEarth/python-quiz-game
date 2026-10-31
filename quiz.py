"""Quiz model class representing individual quiz items."""

from typing import Any, Dict, List


class Quiz:
    """개별 퀴즈 문제를 표현하는 클래스.

    Attributes:
        question (str): 퀴즈 문제 텍스트
        choices (List[str]): 4개의 객관식 보기 리스트
        answer (int): 1~4 범위의 정답 번호
    """

    def __init__(self, question: str, choices: List[str], answer: int) -> None:
        if not isinstance(question, str) or not question.strip():
            raise ValueError("문제 내용은 비어 있지 않은 문자열이어야 합니다.")

        if not isinstance(choices, list) or len(choices) != 4:
            raise ValueError("선택지는 정확히 4개의 항목으로 구성되어야 합니다.")

        clean_choices = [str(c).strip() for c in choices]
        if any(not c for c in clean_choices):
            raise ValueError("모든 선택지는 비어 있지 않아야 합니다.")

        if not isinstance(answer, int) or answer < 1 or answer > 4:
            raise ValueError("정답 번호는 1부터 4 사이의 정수여야 합니다.")

        self.question: str = question.strip()
        self.choices: List[str] = clean_choices
        self.answer: int = answer

    def is_correct(self, user_answer: int) -> bool:
        """사용자가 입력한 답 번호가 정답과 일치하는지 확인합니다."""
        return self.answer == user_answer

    def get_display_text(self, question_number: int | None = None) -> str:
        """문제와 4개의 선택지를 포맷팅된 문자열로 반환합니다."""
        prefix = f"[문제 {question_number}]\n" if question_number is not None else ""
        lines = [f"{prefix}{self.question}\n"]
        for idx, choice in enumerate(self.choices, start=1):
            lines.append(f"  {idx}. {choice}")
        return "\n".join(lines)

    def to_dict(self) -> Dict[str, Any]:
        """JSON 저장을 위해 딕셔너리 형태로 직렬화합니다."""
        return {
            "question": self.question,
            "choices": self.choices,
            "answer": self.answer,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Quiz":
        """딕셔너리 데이터로부터 Quiz 인스턴스를 역직렬화하여 생성합니다."""
        if not isinstance(data, dict):
            raise TypeError("퀴즈 데이터는 딕셔너리 형태여야 합니다.")
        return cls(
            question=str(data.get("question", "")),
            choices=list(data.get("choices", [])),
            answer=int(data.get("answer", 0)),
        )

    def __repr__(self) -> str:
        return f"Quiz(question={self.question!r}, answer={self.answer})"
