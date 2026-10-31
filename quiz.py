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


def get_default_quizzes() -> List[Quiz]:
    """초기 실행 시 제공되는 5개 이상의 컴퓨터 과학 및 파이썬 기본 퀴즈 데이터셋을 생성합니다."""
    return [
        Quiz(
            question="Python에서 한 번 생성된 요소를 변경할 수 없는 불변(immutable) 시퀀스 자료형은?",
            choices=["list", "tuple", "dict", "set"],
            answer=2,
        ),
        Quiz(
            question="Git에서 원격 저장소의 최신 커밋 이력을 로컬로 내려받아 현재 브랜치에 병합하는 명령어는?",
            choices=["git push", "git clone", "git pull", "git status"],
            answer=3,
        ),
        Quiz(
            question="Python 클래스에서 인스턴스가 생성될 때 자동으로 호출되는 초기화 메서드는?",
            choices=["__init__", "__str__", "__new__", "__call__"],
            answer=1,
        ),
        Quiz(
            question="컴퓨터 아키텍처에서 1바이트(Byte)는 몇 비트(bit)로 구성될까요?",
            choices=["4비트", "8비트", "16비트", "32비트"],
            answer=2,
        ),
        Quiz(
            question="Python에서 파일 등 자원을 안전하게 열고 자동으로 닫아주기 위해 사용하는 문법 키워드는?",
            choices=["try-finally", "with", "lambda", "global"],
            answer=2,
        ),
        Quiz(
            question="다음 중 Python 조건문에서 참(True)으로 평가되는 'Truthy' 값은 무엇일까요?",
            choices=["0", "[] (빈 리스트)", "None", "[0] (숫자 0이 포함된 리스트)"],
            answer=4,
        ),
    ]

