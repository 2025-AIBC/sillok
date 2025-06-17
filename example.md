# 연구 노트: 클라우드 네이티브 네트워킹 성능 비교

**작성일**: 2025-06-11  
**연구자**: (가정) 클라우드 인프라 연구팀

---

## 1. 연구 배경 및 목적

-   **배경**: 서비스 마이크로서비스화 확산에 따라 컨테이너 네트워킹 성능이 전체 시스템 성능에 미치는 영향이 커지고 있음.
-   **목적**: Kubernetes 클러스터에서 CNI 플러그인(Cilium vs. Calico) 간 네트워크 대역폭 및 레이턴시 성능을 정량적으로 비교·분석하여, 고성능·고가용성 아키텍처 설계 가이드라인 도출.

---

## 2. 연구 가설

1. **가설 1**: eBPF 기반 Cilium이 Calico보다 패킷 처리 효율이 높아 레이턴시 저하 및 쓰루풋 향상을 제공할 것이다.
2. **가설 2**: Pod 간 통신 시 네트워크 정책 적용 오버헤드가 Cilium에서 더 낮게 관측될 것이다.

---

## 3. 실험 환경

| 구성 요소         | 세부 내용                                 |
| ----------------- | ----------------------------------------- |
| 클러스터 매니저   | Kubernetes v1.27                          |
| CNI 플러그인      | - Cilium v1.14<br>- Calico v3.27          |
| 클라우드 인스턴스 | AWS EC2 m5.large (2vCPU, 8GB RAM) × 3대   |
| OS 및 커널        | Ubuntu 22.04 LTS, Linux 5.19              |
| 벤치마크 툴       | `iperf3`, `ping`, `kubectl exec` 스크립트 |
| 네트워크 설정     | MTU=1500, VPC 내 동일 AZ                  |

---

## 4. 실험 방법

1. 각 CNI 별로 동일한 클러스터 구성(bare-metal emulation) 수행
2. Pod A ⇄ Pod B 간 `iperf3` TCP 벤치마크 10회 반복 측정
3. Pod 간 ICMP 레이턴시 측정(ping, 100패킷)
4. 네트워크 정책 적용 전·후 성능 비교
5. 수집된 로그는 Prometheus에 저장, Grafana 대시보드로 시각화

```bash
# 예시: iperf3 서버 실행
kubectl run iperf-server --image=networkstatic/iperf3 -o yaml --dry-run=client > iperf-server.yaml
kubectl apply -f iperf-server.yaml
# 클라이언트 벤치
kubectl run iperf-client --rm -it --image=networkstatic/iperf3 -- \
    iperf3 -c iperf-server.default.svc.cluster.local -t 30
```
