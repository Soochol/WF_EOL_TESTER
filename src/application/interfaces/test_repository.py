"""
Test Repository Interface

Interface for test data persistence.
"""

from abc import ABC, abstractmethod
from typing import Optional, List
from domain.entities.eol_test import EOLTest


class TestRepository(ABC):
    """테스트 데이터 저장소 인터페이스"""
    
    @abstractmethod
    async def save(self, test: EOLTest) -> EOLTest:
        """
        테스트 저장
        
        Args:
            test: 저장할 테스트
            
        Returns:
            저장된 테스트
        """
        pass
    
    @abstractmethod
    async def update(self, test: EOLTest) -> EOLTest:
        """
        테스트 수정
        
        Args:
            test: 수정할 테스트
            
        Returns:
            수정된 테스트
        """
        pass
    
    @abstractmethod
    async def find_by_id(self, test_id: str) -> Optional[EOLTest]:
        """
        ID로 테스트 조회
        
        Args:
            test_id: 테스트 ID
            
        Returns:
            조회된 테스트 (없으면 None)
        """
        pass
    
    @abstractmethod
    async def find_by_dut_id(self, dut_id: str) -> List[EOLTest]:
        """
        DUT ID로 테스트 목록 조회
        
        Args:
            dut_id: DUT ID
            
        Returns:
            테스트 목록
        """
        pass
    
    @abstractmethod
    async def delete(self, test_id: str) -> bool:
        """
        테스트 삭제
        
        Args:
            test_id: 테스트 ID
            
        Returns:
            삭제 성공 여부
        """
        pass