"""Storage management module for persisting quiz state to state.json."""

import json
import os
from typing import Any, Dict, List, Tuple
from quiz import Quiz, get_default_quizzes


class QuizStorage:
    """state.json 파일의 읽기, 쓰기 및 손상 복구를 전담하는 클래스.

    Attributes:
        file_path (str): 상태 저장 파일 경로 (기본값: 'state.json')
    """

    def __init__(self, file_path: str = "state.json") -> None:
        self.file_path = file_path

    def load_state(self) -> Tuple[List[Quiz], int, str]:
        """state.json 파일에서 퀴즈 목록과 최고 점수를 불러옵니다.

        Returns:
            Tuple[List[Quiz], int, str]: (퀴즈 객체 목록, 최고 점수, 로드 상태 메시지)
        """
        if not os.path.exists(self.file_path):
            default_quizzes = get_default_quizzes()
            default_best_score = 0
            self.save_state(default_quizzes, default_best_score)
            return (
                default_quizzes,
                default_best_score,
                f"📂 저장된 데이터 파일이 없어 기본 퀴즈({len(default_quizzes)}개)로 새로 생성했습니다.",
            )

        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                data: Dict[str, Any] = json.load(f)

            if not isinstance(data, dict):
                raise ValueError("JSON 최상위 데이터는 객체(dict)여야 합니다.")

            quizzes_data = data.get("quizzes")
            best_score = data.get("best_score", 0)

            if not isinstance(quizzes_data, list):
                raise ValueError("'quizzes' 필드가 리스트 형태가 아닙니다.")

            if not isinstance(best_score, int) or best_score < 0:
                best_score = 0

            quizzes: List[Quiz] = []
            for item in quizzes_data:
                quizzes.append(Quiz.from_dict(item))

            if not quizzes:
                raise ValueError("저장된 퀴즈 목록이 비어 있습니다.")

            return (
                quizzes,
                best_score,
                f"📂 저장된 데이터를 성공적으로 불러왔습니다. (퀴즈 {len(quizzes)}개, 최고점수 {best_score}점)",
            )

        except (json.JSONDecodeError, ValueError, TypeError, KeyError) as e:
            # 파일 손상 또는 스키마 불일치 시 기본 데이터로 자동 복구
            warning_msg = (
                f"⚠️ 저장 데이터({self.file_path})가 손상되었거나 유효하지 않습니다: {e}\n"
                f"기본 퀴즈 데이터로 안전하게 복구합니다."
            )
            default_quizzes = get_default_quizzes()
            default_best_score = 0
            self.save_state(default_quizzes, default_best_score)
            return default_quizzes, default_best_score, warning_msg
        except OSError as e:
            warning_msg = f"⚠️ 파일 읽기 오류가 발생했습니다: {e}. 기본 퀴즈 데이터를 임시 사용합니다."
            return get_default_quizzes(), 0, warning_msg

    def save_state(self, quizzes: List[Quiz], best_score: int) -> bool:
        """현재 퀴즈 목록과 최고 점수를 state.json에 UTF-8 인코딩으로 저장합니다.

        Args:
            quizzes (List[Quiz]): 저장할 퀴즈 객체 목록
            best_score (int): 저장할 최고 점수

        Returns:
            bool: 저장 성공 여부
        """
        payload = {
            "quizzes": [quiz.to_dict() for quiz in quizzes],
            "best_score": best_score,
        }
        try:
            # 안전한 쓰기를 위해 임시 파일 기록 후 교체(원자적 쓰기) 방식도 가능하나,
            # 직관적인 UTF-8 쓰기 수행
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump(payload, f, ensure_ascii=False, indent=2)
            return True
        except OSError as e:
            print(f"❌ 데이터 저장 중 파일 시스템 오류가 발생했습니다: {e}")
            return False
