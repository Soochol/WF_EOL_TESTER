#!/usr/bin/env python3
"""
타이밍 비교 분석

단순 시리얼 통신과 현재 프로젝트 코드의 성능을 비교하여
3초 대기가 필요한 근본 원인을 분석합니다.
"""

import json
import os
import glob
from datetime import datetime
from typing import Dict, List, Optional

class TimingComparator:
    """타이밍 비교 분석기"""
    
    def __init__(self):
        self.simple_results: List[Dict] = []
        self.current_with_delays: List[Dict] = []
        self.current_no_delays: List[Dict] = []
        
    def load_test_results(self) -> bool:
        """테스트 결과 파일들 로드"""
        results_dir = "test_results"
        
        if not os.path.exists(results_dir):
            print(f"❌ 결과 디렉토리가 없습니다: {results_dir}")
            return False
            
        try:
            # 단순 시리얼 테스트 결과
            simple_files = glob.glob(f"{results_dir}/simple_test_results_*.json")
            if simple_files:
                latest_simple = max(simple_files, key=os.path.getctime)
                with open(latest_simple, 'r', encoding='utf-8') as f:
                    simple_data = json.load(f)
                    self.simple_results = simple_data.get("results", [])
                print(f"📂 단순 테스트 결과 로드: {latest_simple}")
            else:
                print("⚠️ 단순 테스트 결과 파일이 없습니다.")
                
            # 현재 코드 (대기 포함) 결과
            with_delays_files = glob.glob(f"{results_dir}/current_code_with_delays_*.json")
            if with_delays_files:
                latest_with_delays = max(with_delays_files, key=os.path.getctime)
                with open(latest_with_delays, 'r', encoding='utf-8') as f:
                    with_delays_data = json.load(f)
                    self.current_with_delays = with_delays_data.get("results", [])
                print(f"📂 현재 코드 (대기 포함) 결과 로드: {latest_with_delays}")
            else:
                print("⚠️ 현재 코드 (대기 포함) 결과 파일이 없습니다.")
                
            # 현재 코드 (대기 없음) 결과
            no_delays_files = glob.glob(f"{results_dir}/current_code_no_delays_*.json")
            if no_delays_files:
                latest_no_delays = max(no_delays_files, key=os.path.getctime)
                with open(latest_no_delays, 'r', encoding='utf-8') as f:
                    no_delays_data = json.load(f)
                    self.current_no_delays = no_delays_data.get("results", [])
                print(f"📂 현재 코드 (대기 없음) 결과 로드: {latest_no_delays}")
            else:
                print("⚠️ 현재 코드 (대기 없음) 결과 파일이 없습니다.")
                
            return True
            
        except Exception as e:
            print(f"❌ 결과 로드 실패: {e}")
            return False
            
    def analyze_response_times(self):
        """응답 시간 분석"""
        print("\n⚡ 응답 시간 분석")
        print("=" * 60)
        
        if self.simple_results:
            print("\n📱 단순 시리얼 통신:")
            total_responses = 0
            total_time = 0
            
            for result in self.simple_results:
                if result.get("success") and "response_time_ms" in result:
                    response_time = result["response_time_ms"]
                    desc = result.get("description", "Unknown")
                    print(f"   {desc}: {response_time:.1f}ms")
                    total_responses += 1
                    total_time += response_time
                    
            if total_responses > 0:
                avg_time = total_time / total_responses
                print(f"   평균 응답 시간: {avg_time:.1f}ms")
            else:
                print("   ❌ 응답 시간 데이터 없음")
        else:
            print("⚠️ 단순 시리얼 테스트 결과 없음")
            
    def analyze_execution_times(self):
        """실행 시간 분석"""
        print("\n🏃 실행 시간 분석")
        print("=" * 60)
        
        datasets = [
            ("현재 코드 (3초 대기)", self.current_with_delays),
            ("현재 코드 (대기 없음)", self.current_no_delays)
        ]
        
        for dataset_name, dataset in datasets:
            if not dataset:
                print(f"\n⚠️ {dataset_name}: 데이터 없음")
                continue
                
            print(f"\n🔧 {dataset_name}:")
            
            total_execution = 0
            total_wait = 0
            total_time = 0
            success_count = 0
            
            for result in dataset:
                if result.get("success"):
                    command = result.get("command", "Unknown")
                    exec_time = result.get("execution_time", 0)
                    wait_time = result.get("wait_time", 0) 
                    total_cmd_time = result.get("total_time", 0)
                    
                    print(f"   {command}:")
                    print(f"     실행: {exec_time*1000:.1f}ms, 대기: {wait_time:.1f}s, 총계: {total_cmd_time:.3f}s")
                    
                    total_execution += exec_time
                    total_wait += wait_time
                    total_time += total_cmd_time
                    success_count += 1
                else:
                    command = result.get("command", "Unknown")
                    error = result.get("error", "Unknown error")
                    print(f"   {command}: ❌ 실패 ({error})")
                    
            if success_count > 0:
                print(f"\n   📊 요약:")
                print(f"     총 실행 시간: {total_execution:.3f}s ({total_execution*1000:.0f}ms)")
                print(f"     총 대기 시간: {total_wait:.3f}s") 
                print(f"     전체 소요 시간: {total_time:.3f}s")
                print(f"     성공률: {success_count}/{len(dataset)} ({success_count/len(dataset)*100:.1f}%)")
                
    def compare_performance(self):
        """성능 비교"""
        print("\n📊 성능 비교")
        print("=" * 60)
        
        # 단순 시리얼 vs 현재 코드 비교
        if self.simple_results and self.current_no_delays:
            simple_responses = [r.get("response_time_ms", 0) for r in self.simple_results if r.get("success")]
            current_executions = [r.get("execution_time", 0) * 1000 for r in self.current_no_delays if r.get("success")]
            
            if simple_responses and current_executions:
                simple_avg = sum(simple_responses) / len(simple_responses)
                current_avg = sum(current_executions) / len(current_executions)
                
                print(f"\n⚡ 평균 명령 처리 시간:")
                print(f"   단순 시리얼: {simple_avg:.1f}ms")
                print(f"   현재 코드: {current_avg:.1f}ms")
                print(f"   오버헤드: +{current_avg - simple_avg:.1f}ms ({((current_avg/simple_avg)-1)*100:.1f}%)")
                
        # 대기시간 효과 분석
        if self.current_with_delays and self.current_no_delays:
            with_delays_time = sum([r.get("total_time", 0) for r in self.current_with_delays if r.get("success")])
            no_delays_time = sum([r.get("total_time", 0) for r in self.current_no_delays if r.get("success")])
            
            with_delays_success = len([r for r in self.current_with_delays if r.get("success")])
            no_delays_success = len([r for r in self.current_no_delays if r.get("success")])
            
            print(f"\n🔄 대기시간 효과:")
            print(f"   3초 대기 포함: {with_delays_time:.3f}s (성공: {with_delays_success}/{len(self.current_with_delays)})")
            print(f"   대기시간 없음: {no_delays_time:.3f}s (성공: {no_delays_success}/{len(self.current_no_delays)})")
            
            if with_delays_success > 0 and no_delays_success > 0:
                time_saved = with_delays_time - no_delays_time
                success_rate_diff = (no_delays_success/len(self.current_no_delays)) - (with_delays_success/len(self.current_with_delays))
                
                print(f"   시간 단축: {time_saved:.3f}s ({(time_saved/with_delays_time)*100:.1f}%)")
                print(f"   성공률 변화: {success_rate_diff*100:+.1f}%")
                
                if no_delays_success == len(self.current_no_delays):
                    print(f"   ✅ 대기시간 없이도 100% 성공!")
                elif no_delays_success < with_delays_success:
                    print(f"   ⚠️ 대기시간 제거 시 성공률 감소")
                    
    def identify_bottlenecks(self):
        """병목 지점 식별"""
        print("\n🔍 병목 지점 분석")
        print("=" * 60)
        
        # 현재 코드의 실행 시간이 단순 시리얼보다 긴 이유 분석
        if self.simple_results and self.current_no_delays:
            print("\n🚩 잠재적 병목 요인:")
            
            simple_avg = sum([r.get("response_time_ms", 0) for r in self.simple_results if r.get("success")]) / max(1, len([r for r in self.simple_results if r.get("success")]))
            current_avg = sum([r.get("execution_time", 0) * 1000 for r in self.current_no_delays if r.get("success")]) / max(1, len([r for r in self.current_no_delays if r.get("success")]))
            
            overhead = current_avg - simple_avg
            
            if overhead > 10:  # 10ms 이상 차이
                print(f"   1. 코드 오버헤드: +{overhead:.1f}ms")
                print(f"      - 비동기 처리 (async/await)")
                print(f"      - 연결 상태 확인 (_ensure_connected)")
                print(f"      - 복잡한 패킷 검증")
                print(f"      - 버퍼 관리 및 동기화")
                print(f"      - 재시도 로직")
                
            # 실패한 명령 분석
            failed_commands = [r for r in self.current_no_delays if not r.get("success")]
            if failed_commands:
                print(f"\n   2. 실패한 명령들:")
                for cmd in failed_commands:
                    print(f"      - {cmd.get('command', 'Unknown')}: {cmd.get('error', 'Unknown error')}")
                    
    def generate_recommendations(self):
        """개선 권장사항 생성"""
        print("\n💡 개선 권장사항")
        print("=" * 60)
        
        recommendations = []
        
        # 성공률 기반 권장사항
        if self.current_no_delays:
            no_delay_success_rate = len([r for r in self.current_no_delays if r.get("success")]) / len(self.current_no_delays)
            
            if no_delay_success_rate >= 1.0:
                recommendations.append("✅ 대기시간 완전 제거 가능 - 100% 성공률 달성")
            elif no_delay_success_rate >= 0.8:
                recommendations.append("⚠️ 대기시간 부분 제거 가능 - 일부 명령만 대기 필요")
            else:
                recommendations.append("❌ 대기시간 필요 - 안정성 확보 우선")
                
        # 성능 기반 권장사항
        if self.simple_results and self.current_no_delays:
            simple_avg = sum([r.get("response_time_ms", 0) for r in self.simple_results if r.get("success")]) / max(1, len([r for r in self.simple_results if r.get("success")]))
            current_avg = sum([r.get("execution_time", 0) * 1000 for r in self.current_no_delays if r.get("success")]) / max(1, len([r for r in self.current_no_delays if r.get("success")]))
            
            if current_avg > simple_avg * 2:  # 2배 이상 느림
                recommendations.append("🔧 코드 최적화 필요 - 과도한 오버헤드 발생")
                recommendations.append("   - 버퍼 클리어링 로직 간소화")
                recommendations.append("   - STX 동기화 최적화") 
                recommendations.append("   - 패킷 검증 단순화")
                recommendations.append("   - 재시도 로직 조정")
                
        # 구체적 실행 방안
        print("\n🎯 즉시 실행 가능한 개선사항:")
        for i, rec in enumerate(recommendations, 1):
            print(f"   {i}. {rec}")
            
        print(f"\n📋 단계별 실행 계획:")
        print(f"   1단계: mcu_command_stabilization = 0.1초로 설정")
        print(f"   2단계: 성공률 확인 후 0초로 단축")
        print(f"   3단계: 필요시 명령별 개별 대기시간 설정")
        print(f"   4단계: 코드 오버헤드 최적화")
        
    def save_comparison_report(self):
        """비교 분석 보고서 저장"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"test_results/timing_comparison_report_{timestamp}.md"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("# MCU 통신 타이밍 비교 분석 보고서\n\n")
                f.write(f"생성일시: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                
                # 요약 정보 작성
                if self.simple_results:
                    simple_avg = sum([r.get("response_time_ms", 0) for r in self.simple_results if r.get("success")]) / max(1, len([r for r in self.simple_results if r.get("success")]))
                    f.write(f"## 📊 테스트 결과 요약\n\n")
                    f.write(f"- **단순 시리얼 통신**: 평균 {simple_avg:.1f}ms 응답\n")
                    
                if self.current_no_delays:
                    current_avg = sum([r.get("execution_time", 0) * 1000 for r in self.current_no_delays if r.get("success")]) / max(1, len([r for r in self.current_no_delays if r.get("success")]))
                    success_rate = len([r for r in self.current_no_delays if r.get("success")]) / len(self.current_no_delays)
                    f.write(f"- **현재 코드 (대기 없음)**: 평균 {current_avg:.1f}ms 실행, 성공률 {success_rate*100:.1f}%\n")
                    
                if self.current_with_delays:
                    total_time = sum([r.get("total_time", 0) for r in self.current_with_delays if r.get("success")])
                    f.write(f"- **현재 코드 (3초 대기)**: 총 {total_time:.3f}s 소요\n")
                    
                f.write(f"\n## 🎯 결론\n\n")
                
                if self.current_no_delays:
                    no_delay_success_rate = len([r for r in self.current_no_delays if r.get("success")]) / len(self.current_no_delays)
                    if no_delay_success_rate >= 1.0:
                        f.write("**3초 대기시간 제거 권장** - 성능 향상 가능\n\n")
                    else:
                        f.write("**점진적 대기시간 단축 권장** - 안정성 확보 필요\n\n")
                        
            print(f"📋 비교 분석 보고서 저장: {filename}")
            
        except Exception as e:
            print(f"❌ 보고서 저장 실패: {e}")

def main():
    """메인 실행"""
    print("📊 MCU 통신 타이밍 비교 분석")
    print("=" * 40)
    
    comparator = TimingComparator()
    
    # 테스트 결과 로드
    if not comparator.load_test_results():
        print("테스트를 먼저 실행하세요:")
        print("1. python simple_serial_test.py")
        print("2. python current_code_test.py")
        return
        
    # 분석 실행
    comparator.analyze_response_times()
    comparator.analyze_execution_times()
    comparator.compare_performance()
    comparator.identify_bottlenecks()
    comparator.generate_recommendations()
    
    # 보고서 저장
    comparator.save_comparison_report()
    
    print(f"\n🎉 분석 완료!")

if __name__ == "__main__":
    main()