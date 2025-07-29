"""
Test Result Repository Interface

Interface for test result data persistence.
"""

from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
from domain.entities.eol_test import EOLTest


class TestResultRepository(ABC):
    """테스트 결과 데이터 저장소 인터페이스"""
    
    @abstractmethod
    async def save(self, test: EOLTest) -> EOLTest:
        """
        테스트 결과 저장
        
        Args:
            test: 저장할 테스트 결과
            
        Returns:
            저장된 테스트 결과
        """
        pass
    
    @abstractmethod
    async def update(self, test: EOLTest) -> EOLTest:
        """
        테스트 결과 수정
        
        Args:
            test: 수정할 테스트 결과
            
        Returns:
            수정된 테스트 결과
        """
        pass
    
    @abstractmethod
    async def find_by_id(self, test_id: str) -> Optional[EOLTest]:
        """
        ID로 테스트 결과 조회
        
        Args:
            test_id: 테스트 ID
            
        Returns:
            조회된 테스트 결과 (없으면 None)
        """
        pass
    
    @abstractmethod
    async def find_by_dut_id(self, dut_id: str) -> List[EOLTest]:
        """
        DUT ID로 테스트 결과 목록 조회
        
        Args:
            dut_id: DUT ID
            
        Returns:
            테스트 결과 목록
        """
        pass
    
    @abstractmethod
    async def delete(self, test_id: str) -> None:
        """
        테스트 결과 삭제
        
        Args:
            test_id: 테스트 ID
            
        Raises:
            RepositoryAccessError: If deletion fails
            ConfigurationNotFoundError: If test with given ID does not exist
        """
        pass
    
    @abstractmethod
    async def get_all_tests(self) -> List[Dict[str, Any]]:
        """
        모든 테스트 조회 (관리용)
        
        Returns:
            모든 테스트 딕셔너리 리스트
        """
        pass
    
    @abstractmethod
    async def cleanup_old_tests(self, days: int = 30) -> int:
        """
        오래된 테스트 정리
        
        Args:
            days: 보관 기간 (일)
            
        Returns:
            정리된 테스트 수
        """
        pass