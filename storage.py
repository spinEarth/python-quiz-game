"""Storage management module for persisting quiz state to state.json."""

import datetime
import json
import os
import shutil
from typing import Any, Dict, List, Optional, Tuple
from quiz import Quiz, get_default_quizzes


class QuizStorage:
    """state.json 파일의 읽기, 쓰기 및 버전/백업 기반 손상 복구를 전담하는 클래스.

    Attributes:
        file_path (str): 상태 저장 파일 경로 (기본값: 'state.json')
        backup_path (str): 직전 정상 상태 백업 파일 경로
    """

    def __init__(self, file_path: str = "state.json") -> None:
        self.file_path = file_path
        self.backup_path = f"{file_path}.bak"

    def _preserve_corrupted_file(self) -> Optional[str]:
        """손상된 원본 파일을 타임스탬프가 포함된 이름으로 격리 보존합니다.

        Returns:
            Optional[str]: 생성된 격리 백업 파일 경로 (실패 시 None)
        """
        if not os.path.exists(self.file_path):
            return None

        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        corrupted_copy_path = f"{self.file_path}.corrupted.{timestamp}"
        try:
            shutil.copy2(self.file_path, corrupted_copy_path)
            return corrupted_copy_path
        except OSError as e:
            print(f"⚠️ 손상 파일 백업 복사 중 오류 발생: {e}")
            return None

    def _try_load_from_file(self, target_path: str) -> Tuple[List[Quiz], int]:
        """지정된 파일 경로에서 JSON 데이터를 파싱하여 퀴즈 객체 목록과 최고 점수를 추출합니다.

        Raises:
            FileNotFoundError, json.JSONDecodeError, ValueError, TypeError, KeyError
        """
        with open(target_path, "r", encoding="utf-8") as f:
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

        return quizzes, best_score

    def load_state(self) -> Tuple[List[Quiz], int, str]:
        """state.json 파일에서 퀴즈 목록과 최고 점수를 불러옵니다.

        손상 감지 시:
        1. 손상된 원본 파일을 state.json.corrupted.<timestamp>로 보존 격리합니다.
        2. 직전 정상 백업 파일(state.json.bak)이 존재하면 해당 백업으로부터 우선 복구합니다.
        3. 백업본도 없거나 손상되었을 경우 기본 퀴즈 데이터셋으로 안전하게 재초기화합니다.

        Returns:
            Tuple[List[Quiz], int, str]: (퀴즈 객체 목록, 최고 점수, 로드 상태 메시지)
        """
        if not os.path.exists(self.file_path):
            # 파일이 아예 없을 때: 백업본이 있는지 먼저 확인
            if os.path.exists(self.backup_path):
                try:
                    quizzes, best_score = self._try_load_from_file(self.backup_path)
                    self.save_state(quizzes, best_score, create_backup=False)
                    return (
                        quizzes,
                        best_score,
                        f"📂 메인 파일이 없어 정상 백업 파일({self.backup_path})로부터 복구했습니다. (퀴즈 {len(quizzes)}개)",
                    )
                except Exception:
                    pass

            # 파일도 없고 백업도 없으면 기본 데이터 생성
            default_quizzes = get_default_quizzes()
            default_best_score = 0
            self.save_state(default_quizzes, default_best_score, create_backup=False)
            return (
                default_quizzes,
                default_best_score,
                f"📂 저장된 데이터 파일이 없어 기본 퀴즈({len(default_quizzes)}개)로 새로 생성했습니다.",
            )

        try:
            quizzes, best_score = self._try_load_from_file(self.file_path)
            return (
                quizzes,
                best_score,
                f"📂 저장된 데이터를 성공적으로 불러왔습니다. (퀴즈 {len(quizzes)}개, 최고점수 {best_score}점)",
            )

        except (json.JSONDecodeError, ValueError, TypeError, KeyError) as e:
            # 1단계: 손상된 원본 파일 격리 백업 (원본 보존)
            preserved_path = self._preserve_corrupted_file()
            backup_note = f" (손상 원본은 '{preserved_path}'에 보존되었습니다.)" if preserved_path else ""

            # 2단계: 기존 정상 백업본(.bak)으로부터 복구 시도
            if os.path.exists(self.backup_path):
                try:
                    backup_quizzes, backup_score = self._try_load_from_file(self.backup_path)
                    self.save_state(backup_quizzes, backup_score, create_backup=False)
                    warning_msg = (
                        f"⚠️ 저장 데이터({self.file_path})가 손상되었습니다: {e}{backup_note}\n"
                        f"✅ 직전 정상 백업({self.backup_path})에서 상태를 성공적으로 복구했습니다! "
                        f"(퀴즈 {len(backup_quizzes)}개, 최고점수 {backup_score}점)"
                    )
                    return backup_quizzes, backup_score, warning_msg
                except Exception as backup_err:
                    print(f"⚠️ 백업 파일 로드 시도 중 오류 발생: {backup_err}")

            # 3단계: 백업본도 사용 불가 시 기본 퀴즈 데이터로 복구
            warning_msg = (
                f"⚠️ 저장 데이터({self.file_path})가 손상되었거나 유효하지 않습니다: {e}{backup_note}\n"
                f"기본 퀴즈 데이터로 안전하게 복구(초기화)합니다."
            )
            default_quizzes = get_default_quizzes()
            default_best_score = 0
            self.save_state(default_quizzes, default_best_score, create_backup=False)
            return default_quizzes, default_best_score, warning_msg

        except OSError as e:
            warning_msg = f"⚠️ 파일 읽기 중 OS 오류가 발생했습니다: {e}. 기본 퀴즈 데이터를 임시 사용합니다."
            return get_default_quizzes(), 0, warning_msg

    def save_state(
        self, quizzes: List[Quiz], best_score: int, create_backup: bool = True
    ) -> bool:
        """현재 퀴즈 목록과 최고 점수를 원자적(Atomic) 쓰기 방식으로 state.json에 저장하고 정상 백업본을 갱신합니다.

        Args:
            quizzes (List[Quiz]): 저장할 퀴즈 객체 목록
            best_score (int): 저장할 최고 점수
            create_backup (bool): 저장 성공 후 최신 정상 백업본(.bak) 갱신 여부

        Returns:
            bool: 저장 성공 여부
        """
        payload = {
            "quizzes": [quiz.to_dict() for quiz in quizzes],
            "best_score": best_score,
        }

        # 1. 임시 파일 작성 후 원자적 교체(atomic replace) 수행
        temp_file_path = f"{self.file_path}.tmp"
        try:
            with open(temp_file_path, "w", encoding="utf-8") as f:
                json.dump(payload, f, ensure_ascii=False, indent=2)
                f.flush()
                os.fsync(f.fileno())

            # 원자적으로 원본 파일과 교체 (쓰기 도중 크래시 발생해도 원본 무손상)
            os.replace(temp_file_path, self.file_path)

            # 2. 저장이 성공적으로 완료된 후 최신 유효 스냅샷 백업(.bak) 갱신
            if create_backup:
                try:
                    shutil.copy2(self.file_path, self.backup_path)
                except OSError as backup_err:
                    print(f"⚠️ 백업본 동기화 중 경고: {backup_err}")

            return True
        except OSError as e:
            print(f"❌ 데이터 저장 중 파일 시스템 오류가 발생했습니다: {e}")
            if os.path.exists(temp_file_path):
                try:
                    os.remove(temp_file_path)
                except OSError:
                    pass
            return False
