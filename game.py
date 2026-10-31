"""QuizGame class and interactive game loop.

This module coordinates quiz interactions, manages runtime game state,
validates user input according to mission specifications, and handles
graceful termination on interrupt signals.
"""

import sys
from typing import List, Optional
from quiz import Quiz
from storage import QuizStorage


class QuizGame:
    """퀴즈 게임의 전체 흐름과 사용자 인터랙션을 관리하는 컨트롤러 클래스.

    Attributes:
        storage (QuizStorage): 상태 저장 및 불러오기를 담당하는 객체
        quizzes (List[Quiz]): 현재 등록된 퀴즈 목록
        best_score (int): 기록된 최고 점수 (0~100)
        is_running (bool): 메인 메뉴 루프 실행 플래그
    """

    MENU_OPTIONS = {
        1: "퀴즈 풀기",
        2: "퀴즈 추가",
        3: "퀴즈 목록",
        4: "점수 확인",
        5: "종료",
    }

    def __init__(self, storage: Optional[QuizStorage] = None) -> None:
        self.storage = storage or QuizStorage("state.json")
        self.quizzes: List[Quiz] = []
        self.best_score: int = 0
        self.is_running: bool = False
        self.load_game_data()

    def load_game_data(self) -> None:
        """state.json 파일로부터 게임 데이터(퀴즈 목록, 최고 점수)를 적재합니다."""
        self.quizzes, self.best_score, load_message = self.storage.load_state()
        print(load_message)

    def save_game_data(self) -> bool:
        """현재 게임 상태를 state.json 파일에 저장합니다."""
        return self.storage.save_state(self.quizzes, self.best_score)

    def prompt_int(self, prompt_text: str, min_val: int, max_val: int) -> int:
        """공통 입력 예외 처리가 적용된 정수 입력 도우미 메서드.

        요구사항 충족:
        - 입력 앞뒤 공백 제거 (strip)
        - 빈 입력(Enter) 처리
        - 정수 변환 불가(abc 등) 처리
        - 허용 범위 밖 숫자(범위 초과/미만) 처리
        - 유효할 때까지 친절한 안내 후 재입력

        Args:
            prompt_text (str): 사용자에게 보여줄 안내 문구
            min_val (int): 허용 최소 정수
            max_val (int): 허용 최대 정수

        Returns:
            int: 검증을 통과한 정수값
        """
        while True:
            raw_input = input(prompt_text).strip()

            if not raw_input:
                print("⚠️ 입력값이 비어 있습니다. 숫자를 입력해 주세요.\n")
                continue

            try:
                val = int(raw_input)
            except ValueError:
                print(f"⚠️ 잘못된 입력입니다. {min_val}~{max_val} 사이의 숫자를 입력하세요.\n")
                continue

            if val < min_val or val > max_val:
                print(
                    f"⚠️ 허용 범위를 벗어났습니다. {min_val}~{max_val} 사이의 숫자를 입력하세요.\n"
                )
                continue

            return val

    def prompt_non_empty_str(self, prompt_text: str) -> str:
        """공백을 제외한 유효 문자열을 입력받는 도우미 메서드."""
        while True:
            text = input(prompt_text).strip()
            if not text:
                print("⚠️ 빈 값은 입력할 수 없습니다. 내용을 입력해 주세요.\n")
                continue
            return text

    def display_menu(self) -> None:
        """메인 콘솔 메뉴를 양식에 맞춰 출력합니다."""
        print()
        print("=" * 40)
        print("        🎯 나만의 퀴즈 게임 🎯")
        print("=" * 40)
        for num, title in self.MENU_OPTIONS.items():
            print(f"{num}. {title}")
        print("=" * 40)

    def handle_menu_selection(self, choice: int) -> None:
        """선택한 메뉴 번호에 따라 개별 핸들러 메서드로 분기합니다."""
        handlers = {
            1: self.play_quiz,
            2: self.add_quiz,
            3: self.show_quizzes,
            4: self.show_best_score,
            5: self.exit_game,
        }
        handler = handlers.get(choice)
        if handler:
            handler()

    def play_quiz(self) -> None:
        """저장된 퀴즈를 출제하고, 정답 여부를 판별하여 점수를 산출 및 갱신합니다."""
        if not self.quizzes:
            print("\n⚠️ 등록된 퀴즈가 없습니다. 먼저 퀴즈를 추가해 주세요!")
            return

        total_questions = len(self.quizzes)
        print(f"\n📝 퀴즈를 시작합니다! (총 {total_questions}문제)")

        correct_count = 0
        for idx, quiz in enumerate(self.quizzes, start=1):
            print("\n" + "-" * 40)
            print(quiz.get_display_text(question_number=idx))
            print()
            user_answer = self.prompt_int("정답 입력 (1-4): ", 1, 4)

            if quiz.is_correct(user_answer):
                print("✅ 정답입니다!")
                correct_count += 1
            else:
                correct_choice_text = quiz.choices[quiz.answer - 1]
                print(
                    f"❌ 오답입니다! (정답: {quiz.answer}번 - {correct_choice_text})"
                )

        score = int((correct_count / total_questions) * 100)

        print("\n" + "=" * 40)
        print(f"🏆 결과: {total_questions}문제 중 {correct_count}문제 정답! ({score}점)")

        if score > self.best_score:
            print(f"🎉 축하합니다! 새로운 최고 점수입니다! (이전: {self.best_score}점 -> 현재: {score}점)")
            self.best_score = score
            self.save_game_data()
        else:
            print(f"📌 현재 최고 점수: {self.best_score}점")
        print("=" * 40)

    def add_quiz(self) -> None:
        """사용자로부터 신규 문제/선택지/정답을 입력받아 검증 후 저장합니다."""
        print("\n📌 새로운 퀴즈를 추가합니다.")

        question = self.prompt_non_empty_str("문제를 입력하세요: ")

        choices: List[str] = []
        for i in range(1, 5):
            choice_text = self.prompt_non_empty_str(f"선택지 {i}: ")
            choices.append(choice_text)

        answer = self.prompt_int("정답 번호 (1-4): ", 1, 4)

        try:
            new_quiz = Quiz(question=question, choices=choices, answer=answer)
            self.quizzes.append(new_quiz)
            if self.save_game_data():
                print(f"\n✅ 퀴즈가 성공적으로 추가 및 저장되었습니다! (총 {len(self.quizzes)}개)")
            else:
                print("\n⚠️ 퀴즈가 메모리에 추가되었으나 파일 저장에 실패했습니다.")
        except ValueError as err:
            print(f"\n❌ 퀴즈 등록 중 검증 오류가 발생했습니다: {err}")

    def show_quizzes(self) -> None:
        """현재 등록된 모든 퀴즈 목록을 번호순으로 출력합니다."""
        if not self.quizzes:
            print("\n⚠️ 등록된 퀴즈가 없습니다.")
            return

        print(f"\n📋 등록된 퀴즈 목록 (총 {len(self.quizzes)}개)")
        print("-" * 40)
        for idx, quiz in enumerate(self.quizzes, start=1):
            print(f"[{idx}] {quiz.question}")
        print("-" * 40)

    def show_best_score(self) -> None:
        """기록된 최고 점수를 확인하고 미플레이 상태를 안내합니다."""
        print()
        if self.best_score == 0:
            print("📌 아직 달성한 최고 점수 기록이 없습니다 (0점).")
            print("   메뉴 1번을 선택해 퀴즈를 풀고 최고 점수를 기록해 보세요!")
        else:
            print(f"🏆 현재 기록된 최고 점수: {self.best_score}점")

    def exit_game(self) -> None:
        """게임을 정상 저장 후 종료합니다."""
        print("\n💾 현재 게임 상태를 저장하는 중...")
        self.save_game_data()
        print("👋 퀴즈 게임을 종료합니다. 이용해 주셔서 감사합니다!")
        self.is_running = False

    def safe_shutdown(self) -> None:
        """비정상 시그널(Ctrl+C, EOF) 감지 시 안전하게 저장 후 종료합니다."""
        print("\n\n⚠️ 안전 종료 신호(KeyboardInterrupt / EOF)가 감지되었습니다.")
        print("💾 상태를 안전하게 저장한 뒤 프로그램을 종료합니다...")
        self.save_game_data()
        print("👋 안전하게 종료되었습니다. 안녕히 가세요!")
        self.is_running = False

    def run(self) -> None:
        """메인 실행 루프입니다."""
        self.is_running = True
        try:
            while self.is_running:
                self.display_menu()
                choice = self.prompt_int("선택: ", 1, 5)
                self.handle_menu_selection(choice)
        except (KeyboardInterrupt, EOFError):
            self.safe_shutdown()
