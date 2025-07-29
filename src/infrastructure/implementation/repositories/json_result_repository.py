"""
JSON Result Repository

Simple file-based test result data persistence using JSON format.
"""

import json
from datetime import datetime
from typing import Optional, List, Dict, Any
from pathlib import Path
from loguru import logger

from application.interfaces.repository.test_result_repository import TestResultRepository
from domain.entities.eol_test import EOLTest
from domain.value_objects.identifiers import TestId
from domain.exceptions import RepositoryAccessError, ConfigurationNotFoundError


class JsonResultRepository(TestResultRepository):
    """JSON 파일 기반 테스트 결과 저장소"""

    def __init__(self, data_dir: str = "data/tests", auto_save: bool = True):
        """
        초기화

        Args:
            data_dir: 데이터 저장 디렉토리
            auto_save: 자동 저장 여부
        """
        self._data_dir = Path(data_dir)
        self._auto_save = auto_save
        self._tests_cache: Dict[str, Dict[str, Any]] = {}

        # 디렉토리 생성
        self._data_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"JsonResultRepository initialized at {self._data_dir}")

    async def save(self, test: EOLTest) -> EOLTest:
        """
        테스트 저장

        Args:
            test: 저장할 테스트

        Returns:
            저장된 테스트
        """
        test_dict = await self._test_to_dict(test)
        test_id = str(test.test_id)

        # 캐시에 저장
        self._tests_cache[test_id] = test_dict

        if self._auto_save:
            await self._save_to_file(test_id, test_dict)

        logger.debug(f"Test {test_id} saved to repository")
        return test

    async def update(self, test: EOLTest) -> EOLTest:
        """
        테스트 수정

        Args:
            test: 수정할 테스트

        Returns:
            수정된 테스트
        """
        return await self.save(test)  # JSON에서는 save와 update가 동일

    async def find_by_id(self, test_id: str) -> Optional[EOLTest]:
        """
        ID로 테스트 조회

        Args:
            test_id: 테스트 ID

        Returns:
            조회된 테스트 (없으면 None)
        """
        # 캐시에서 먼저 조회
        if test_id in self._tests_cache:
            test_dict = self._tests_cache[test_id]
            return await self._dict_to_test(test_dict)

        # 파일에서 로드
        test_dict = await self._load_from_file(test_id)
        if test_dict:
            self._tests_cache[test_id] = test_dict
            return await self._dict_to_test(test_dict)

        return None

    async def find_by_dut_id(self, dut_id: str) -> List[EOLTest]:
        """
        DUT ID로 테스트 목록 조회

        Args:
            dut_id: DUT ID

        Returns:
            테스트 목록
        """
        tests = []

        # 모든 테스트 파일 스캔
        await self._load_all_tests()

        for test_dict in self._tests_cache.values():
            if test_dict.get("dut", {}).get("dut_id") == dut_id:
                test = await self._dict_to_test(test_dict)
                tests.append(test)

        # 생성 시간으로 정렬 (최신순)
        tests.sort(key=lambda t: t.created_at, reverse=True)

        logger.debug(f"Found {len(tests)} tests for DUT {dut_id}")
        return tests

    async def delete(self, test_id: str) -> None:
        """
        테스트 삭제

        Args:
            test_id: 테스트 ID

        Raises:
            ConfigurationNotFoundError: If test does not exist
            RepositoryAccessError: If deletion fails
        """
        try:
            # 테스트 존재 확인
            file_path = self._get_test_file_path(test_id)
            if not file_path.exists() and test_id not in self._tests_cache:
                raise ConfigurationNotFoundError(
                    f"Test {test_id} not found", config_source=str(file_path)
                )

            # 캐시에서 제거
            if test_id in self._tests_cache:
                del self._tests_cache[test_id]

            # 파일 삭제
            if file_path.exists():
                file_path.unlink()

            logger.debug(f"Test {test_id} deleted from repository")

        except ConfigurationNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Failed to delete test {test_id}: {e}")
            raise RepositoryAccessError(
                f"Failed to delete test {test_id}: {str(e)}",
                config_source=str(self._get_test_file_path(test_id)),
            )

    async def _test_to_dict(self, test: EOLTest) -> Dict[str, Any]:
        """테스트 엔티티를 딕셔너리로 변환"""
        try:
            # EOLTest의 내장 to_dict 메서드를 사용하여 완전한 직렬화
            return test.to_dict()
        except Exception as e:
            logger.error(f"Failed to convert EOLTest to dict: {e}")
            logger.debug(f"Test: {test}")
            raise

    async def _dict_to_test(self, test_dict: Dict[str, Any]) -> EOLTest:
        """딕셔너리를 테스트 엔티티로 변환"""
        try:
            # EOLTest의 from_dict 클래스 메서드를 사용하여 완전한 엔티티 복원
            return EOLTest.from_dict(test_dict)
        except Exception as e:
            logger.error(f"Failed to convert dict to EOLTest: {e}")
            logger.debug(f"Test dict: {test_dict}")
            raise

    async def _save_to_file(self, test_id: str, test_dict: Dict[str, Any]) -> None:
        """테스트 데이터를 파일에 저장"""
        file_path = self._get_test_file_path(test_id)

        try:
            # 디렉토리가 없으면 생성
            file_path.parent.mkdir(parents=True, exist_ok=True)

            # JSON 파일로 저장
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(test_dict, f, indent=2, ensure_ascii=False)

            logger.debug(f"Test {test_id} saved to file {file_path}")

        except Exception as e:
            logger.error(f"Failed to save test {test_id} to file: {e}")
            raise

    async def _load_from_file(self, test_id: str) -> Optional[Dict[str, Any]]:
        """파일에서 테스트 데이터 로드"""
        file_path = self._get_test_file_path(test_id)

        if not file_path.exists():
            return None

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                test_dict = json.load(f)

            logger.debug(f"Test {test_id} loaded from file {file_path}")
            return test_dict

        except Exception as e:
            logger.error(f"Failed to load test {test_id} from file: {e}")
            return None

    async def _load_all_tests(self) -> None:
        """모든 테스트 파일을 캐시로 로드"""
        if not self._data_dir.exists():
            return

        for file_path in self._data_dir.glob("*.json"):
            test_id = file_path.stem

            if test_id not in self._tests_cache:
                test_dict = await self._load_from_file(test_id)
                if test_dict:
                    self._tests_cache[test_id] = test_dict

    def _get_test_file_path(self, test_id: str) -> Path:
        """테스트 ID에 대한 파일 경로 반환"""
        return self._data_dir / f"{test_id}.json"

    async def get_all_tests(self) -> List[Dict[str, Any]]:
        """
        모든 테스트 조회 (관리용)

        Returns:
            모든 테스트 딕셔너리 리스트
        """
        await self._load_all_tests()
        return list(self._tests_cache.values())

    async def cleanup_old_tests(self, days: int = 30) -> int:
        """
        오래된 테스트 정리

        Args:
            days: 보관 기간 (일)

        Returns:
            정리된 테스트 수
        """
        cutoff_date = datetime.now().timestamp() - (days * 24 * 60 * 60)
        deleted_count = 0

        await self._load_all_tests()

        for test_id, test_dict in list(self._tests_cache.items()):
            created_at = test_dict.get("created_at")
            if created_at:
                try:
                    test_date = datetime.fromisoformat(created_at).timestamp()
                    if test_date < cutoff_date:
                        try:
                            await self.delete(test_id)
                            deleted_count += 1
                        except Exception as e:
                            logger.warning(f"Failed to delete old test {test_id}: {e}")
                except Exception as e:
                    logger.warning(f"Failed to parse date for test {test_id}: {e}")

        logger.info(f"Cleaned up {deleted_count} old tests (older than {days} days)")
        return deleted_count
